#!/usr/bin/env python3
"""
Sinh file Test Plan JMeter (.jmx) cho bai kiem thu hieu nang
System Under Test: JSONPlaceholder - https://jsonplaceholder.typicode.com
Chay: python3 scripts/build_test_plan.py
Ket qua: test-plans/sample-shop-performance-test.jmx
Tham so khi chay CLI (co the ghi de bang -J):
  -Jusers=50   so nguoi dung ao (mac dinh 10)
  -Jramp=30    thoi gian ramp-up tinh bang giay (mac dinh 10)
  -Jloops=3    so vong lap moi thread (mac dinh 3)
"""
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "test-plans" / "sample-shop-performance-test.jmx"


def sp(parent, name, value=""):
    e = ET.SubElement(parent, "stringProp", {"name": name})
    e.text = value
    return e


def bp(parent, name, value):
    e = ET.SubElement(parent, "boolProp", {"name": name})
    e.text = "true" if value else "false"
    return e


def cp(parent, name):
    return ET.SubElement(parent, "collectionProp", {"name": name})


def http_sampler(parent_tree, name, path, method="GET", body=None, expected_code="200"):
    sampler = ET.SubElement(parent_tree, "HTTPSamplerProxy", {
        "guiclass": "HttpTestSampleGui", "testclass": "HTTPSamplerProxy",
        "testname": name, "enabled": "true"})
    if body is not None:
        bp(sampler, "HTTPSampler.postBodyRaw", True)
        args = ET.SubElement(sampler, "elementProp", {
            "name": "HTTPsampler.Arguments", "elementType": "Arguments"})
        c = cp(args, "Arguments.arguments")
        arg = ET.SubElement(c, "elementProp", {"name": "", "elementType": "HTTPArgument"})
        bp(arg, "HTTPArgument.always_encode", False)
        sp(arg, "Argument.value", body)
        sp(arg, "Argument.metadata", "=")
    else:
        args = ET.SubElement(sampler, "elementProp", {
            "name": "HTTPsampler.Arguments", "elementType": "Arguments",
            "guiclass": "HTTPArgumentsPanel", "testclass": "Arguments", "enabled": "true"})
        cp(args, "Arguments.arguments")
    sp(sampler, "HTTPSampler.domain", "")
    sp(sampler, "HTTPSampler.port", "")
    sp(sampler, "HTTPSampler.protocol", "")
    sp(sampler, "HTTPSampler.contentEncoding", "")
    sp(sampler, "HTTPSampler.path", path)
    sp(sampler, "HTTPSampler.method", method)
    bp(sampler, "HTTPSampler.follow_redirects", True)
    bp(sampler, "HTTPSampler.auto_redirects", False)
    bp(sampler, "HTTPSampler.use_keepalive", True)
    bp(sampler, "HTTPSampler.DO_MULTIPART_POST", False)
    sp(sampler, "HTTPSampler.embedded_url_re", "")
    sp(sampler, "HTTPSampler.connect_timeout", "")
    sp(sampler, "HTTPSampler.response_timeout", "")

    tree = ET.SubElement(parent_tree, "hashTree")
    # Response Assertion: kiem tra HTTP status code mong doi
    assertion = ET.SubElement(tree, "ResponseAssertion", {
        "guiclass": "AssertionGui", "testclass": "ResponseAssertion",
        "testname": f"Assert HTTP {expected_code}", "enabled": "true"})
    c = cp(assertion, "Asserion.test_strings")
    s = ET.SubElement(c, "stringProp", {"name": "49586"})
    s.text = expected_code
    bp(assertion, "Assertion.custom_message", False)
    sp(assertion, "Assertion.test_field", "Assertion.response_code")
    bp(assertion, "Assertion.assume_success", False)
    # 8 = EQUALS pattern type
    ip = ET.SubElement(assertion, "intProp", {"name": "Assertion.test_type"})
    ip.text = "8"
    ET.SubElement(tree, "hashTree")
    return tree


def build():
    root = ET.Element("jmeterTestPlan", {
        "version": "1.2", "properties": "5.0", "jmeter": "5.6.3"})
    main_tree = ET.SubElement(root, "hashTree")

    # ---------- Test Plan ----------
    tp = ET.SubElement(main_tree, "TestPlan", {
        "guiclass": "TestPlanGui", "testclass": "TestPlan",
        "testname": "Ke hoach kiem thu hieu nang - Sample Shop API", "enabled": "true"})
    sp(tp, "TestPlan.comments",
       "Kiem thu hieu nang Sample Shop REST API (ung dung mau trong repo) bang Apache JMeter 5.6.3. "
       "Tham so hoa: users / ramp / loops qua -J khi chay non-GUI.")
    bp(tp, "TestPlan.functional_mode", False)
    bp(tp, "TestPlan.tearDown_on_shutdown", True)
    bp(tp, "TestPlan.serialize_threadgroups", False)
    udv = ET.SubElement(tp, "elementProp", {
        "name": "TestPlan.user_defined_variables", "elementType": "Arguments",
        "guiclass": "ArgumentsPanel", "testclass": "Arguments", "enabled": "true"})
    cp(udv, "Arguments.arguments")
    sp(tp, "TestPlan.user_define_classpath", "")

    tp_tree = ET.SubElement(main_tree, "hashTree")

    # ---------- Thread Group ----------
    tg = ET.SubElement(tp_tree, "ThreadGroup", {
        "guiclass": "ThreadGroupGui", "testclass": "ThreadGroup",
        "testname": "Thread Group - Nguoi dung ao", "enabled": "true"})
    sp(tg, "ThreadGroup.on_sample_error", "continue")
    lc = ET.SubElement(tg, "elementProp", {
        "name": "ThreadGroup.main_controller", "elementType": "LoopController",
        "guiclass": "LoopControlPanel", "testclass": "LoopController", "enabled": "true"})
    bp(lc, "LoopController.continue_forever", False)
    sp(lc, "LoopController.loops", "${__P(loops,3)}")
    sp(tg, "ThreadGroup.num_threads", "${__P(users,10)}")
    sp(tg, "ThreadGroup.ramp_time", "${__P(ramp,10)}")
    bp(tg, "ThreadGroup.same_user_on_next_iteration", True)
    sp(tg, "ThreadGroup.scheduler", "false")
    sp(tg, "ThreadGroup.duration", "")
    sp(tg, "ThreadGroup.delay", "")

    tg_tree = ET.SubElement(tp_tree, "hashTree")

    # HTTP Request Defaults
    cfg = ET.SubElement(tg_tree, "ConfigTestElement", {
        "guiclass": "HttpDefaultsGui", "testclass": "ConfigTestElement",
        "testname": "HTTP Request Defaults", "enabled": "true"})
    args = ET.SubElement(cfg, "elementProp", {
        "name": "HTTPsampler.Arguments", "elementType": "Arguments",
        "guiclass": "HTTPArgumentsPanel", "testclass": "Arguments", "enabled": "true"})
    cp(args, "Arguments.arguments")
    sp(cfg, "HTTPSampler.domain", "${__P(server,127.0.0.1)}")
    sp(cfg, "HTTPSampler.port", "${__P(port,8089)}")
    sp(cfg, "HTTPSampler.protocol", "http")
    sp(cfg, "HTTPSampler.contentEncoding", "")
    sp(cfg, "HTTPSampler.path", "")
    sp(cfg, "HTTPSampler.concurrentPool", "6")
    sp(cfg, "HTTPSampler.connect_timeout", "5000")
    sp(cfg, "HTTPSampler.response_timeout", "10000")
    ET.SubElement(tg_tree, "hashTree")

    # HTTP Header Manager
    hm = ET.SubElement(tg_tree, "HeaderManager", {
        "guiclass": "HeaderPanel", "testclass": "HeaderManager",
        "testname": "HTTP Header Manager", "enabled": "true"})
    hc = cp(hm, "HeaderManager.headers")
    for hname, hval in [("Content-Type", "application/json; charset=UTF-8"),
                        ("Accept", "application/json"),
                        ("User-Agent", "Apache-JMeter/5.6.3 - Student Performance Test")]:
        h = ET.SubElement(hc, "elementProp", {"name": "", "elementType": "Header"})
        sp(h, "Header.name", hname)
        sp(h, "Header.value", hval)
    ET.SubElement(tg_tree, "hashTree")

    # Uniform Random Timer - think time 100-400ms
    timer = ET.SubElement(tg_tree, "UniformRandomTimer", {
        "guiclass": "UniformRandomTimerGui", "testclass": "UniformRandomTimer",
        "testname": "Think Time - Uniform Random Timer", "enabled": "true"})
    sp(timer, "ConstantTimer.delay", "100")
    sp(timer, "RandomTimer.range", "300")
    ET.SubElement(tg_tree, "hashTree")

    # ---------- Samplers (6 endpoints cua Sample Shop API) ----------
    http_sampler(tg_tree, "GET / - Trang chu", "/", "GET")
    http_sampler(tg_tree, "GET /api/products - Danh sach san pham", "/api/products", "GET")
    http_sampler(tg_tree, "GET /api/products/1 - Chi tiet san pham", "/api/products/1", "GET")
    http_sampler(tg_tree, "GET /api/products/search - Tim kiem", "/api/products/search?q=Laptop", "GET")
    http_sampler(tg_tree, "GET /api/users - Danh sach nguoi dung", "/api/users", "GET")
    http_sampler(tg_tree, "POST /api/orders - Tao don hang", "/api/orders", "POST",
                 body='{"productId": 1, "quantity": 2}',
                 expected_code="201")

    # Luu y ve Listener: Khong nhung Listener GUI (View Results Tree / Summary Report /
    # Aggregate Report) vao file .jmx dung cho chay tai, vi:
    #  1) JMeter khuyen cao tat/bo Listener khi chay load test de tranh ton RAM/CPU.
    #  2) Ket qua duoc ghi bang co -l results.jtl khi chay non-GUI va xem lai bang
    #     Listener trong GUI (mo file .jtl) hoac bang HTML Dashboard (jmeter -g).
    # Khi hoc tren GUI, sinh vien tu them cac Listener nay vao Thread Group (xem README).

    tree_str = ET.ElementTree(root)
    ET.indent(tree_str, space="  ")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree_str.write(f, encoding="utf-8", xml_declaration=False)
    print(f"Da tao: {OUT}")


if __name__ == "__main__":
    build()
