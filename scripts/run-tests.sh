#!/usr/bin/env bash
# ============================================================================
# Chay toan bo 3 kich ban kiem thu hieu nang bang Apache JMeter (che do non-GUI)
# Yeu cau: Java 8+ va Apache JMeter 5.6.x (bien JMETER_HOME hoac jmeter trong PATH)
# Cach dung:  bash scripts/run-tests.sh
# Ket qua:    results/kich-ban-*/results.jtl  va  results/dashboard-*/ (HTML)
# ============================================================================
set -e
cd "$(dirname "$0")/.."

# Mot so moi truong IPv6 gay loi ket noi cho Java -> uu tien IPv4 (an toan o moi noi)
export JVM_ARGS="-Djava.net.preferIPv4Stack=true ${JVM_ARGS:-}"

JMETER_BIN="${JMETER_HOME:+$JMETER_HOME/bin/}jmeter"
command -v "$JMETER_BIN" >/dev/null 2>&1 || { echo "Khong tim thay jmeter. Hay cai Apache JMeter va dat JMETER_HOME."; exit 1; }

# 1) Khoi dong ung dung mau neu chua chay
if ! curl -s http://127.0.0.1:8089/api/health >/dev/null 2>&1; then
  echo "==> Khoi dong Sample Shop tai http://127.0.0.1:8089 ..."
  nohup python3 sample-app/app.py > /tmp/sample-shop.log 2>&1 &
  sleep 1
fi
curl -s http://127.0.0.1:8089/api/health && echo

run_scenario() {
  local name="$1" users="$2" ramp="$3" loops="$4"
  local dir="results/$name"
  local dash="results/dashboard-$name"
  mkdir -p "$dir"
  rm -rf "$dash"
  echo "======================================================================"
  echo "==> $name : users=$users, ramp-up=${ramp}s, loops=$loops"
  "$JMETER_BIN" -n -t test-plans/sample-shop-performance-test.jmx \
    -l "$dir/results.jtl" -j "$dir/jmeter.log" \
    -Jusers="$users" -Jramp="$ramp" -Jloops="$loops"
  echo "==> Sinh HTML Dashboard cho $name ..."
  "$JMETER_BIN" -g "$dir/results.jtl" -o "$dash" -j "$dir/dashboard.log" >/dev/null 2>&1 || \
    echo "    (Bo qua dashboard: can cau hinh jmeter.reportgenerator trong user.properties)"
}

# Kich ban 1 - Co ban (Baseline): tai nhe, lam moc so sanh
run_scenario "kich-ban-1-co-ban-10-users"        10  10 5
# Kich ban 2 - Tai thuong (Load Test): tai ky vong khi van hanh that
run_scenario "kich-ban-2-tai-thuong-50-users"    50  30 5
# Kich ban 3 - Tai nang (Stress Test): vuot tai ky vong, tim diem suy giam
run_scenario "kich-ban-3-stress-100-users"      100  30 5

echo "======================================================================"
echo "Hoan thanh. Xem bao cao tong hop trong README.md va cac file results/*/results.jtl"
