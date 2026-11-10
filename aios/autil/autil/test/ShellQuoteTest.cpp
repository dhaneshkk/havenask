/*
 * Copyright 2014-present Alibaba Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
// Self-contained (no gtest) so it also runs outside the Bazel toolchain, e.g.
//   g++ -std=c++17 -fsanitize=address,undefined -Iaios/autil aios/autil/autil/test/ShellQuoteTest.cpp
//   ./a.out
//
// Besides checking the literal output, every case is round-tripped through a
// real /bin/sh: the quoted word must come back byte-for-byte as one argument,
// which proves no shell syntax inside it was interpreted.

#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

#include "autil/ShellQuote.h"

static int failures = 0;

static void expectEq(const std::string &actual, const std::string &expected, const char *what) {
    if (actual != expected) {
        std::fprintf(stderr, "FAIL %s: got [%s] expected [%s]\n", what, actual.c_str(), expected.c_str());
        ++failures;
    }
}

// Runs: printf '%s' <quoted> ; echo-count of argv, and returns what the shell
// saw as argument #1, plus the argument count.
static std::string roundTrip(const std::string &input, int *argc) {
    std::string cmd = "set -- " + autil::shellQuote(input) + "; printf '%d\\n' \"$#\"; printf '%s' \"$1\"";
    FILE *p = popen(cmd.c_str(), "r");
    if (!p) {
        return "<popen failed>";
    }
    std::string out;
    char buf[256];
    size_t n;
    while ((n = fread(buf, 1, sizeof(buf), p)) > 0) {
        out.append(buf, n);
    }
    pclose(p);
    size_t nl = out.find('\n');
    *argc = nl == std::string::npos ? -1 : std::atoi(out.substr(0, nl).c_str());
    return nl == std::string::npos ? out : out.substr(nl + 1);
}

int main() {
    using autil::shellQuote;

    // Literal encoding.
    expectEq(shellQuote(""), "''", "empty");
    expectEq(shellQuote("abc"), "'abc'", "plain");
    expectEq(shellQuote("a b"), "'a b'", "space");
    expectEq(shellQuote("it's"), "'it'\\''s'", "single quote");
    expectEq(shellQuote("'"), "''\\'''", "lone quote");

    // Hostile inputs must survive a real shell unchanged, as one argument.
    const std::vector<std::string> hostile = {
        "",
        "plain",
        "with space",
        "tab\there",
        "new\nline",
        "semi;colon && rm -rf /tmp/never_run",
        "$(touch /tmp/never_run)",
        "`touch /tmp/never_run`",
        "$HOME ${PATH} $1 $#",
        "back\\slash",
        "glob * ? [a-z]",
        "pipe | redirect > /tmp/never_run < in",
        "'",
        "''",
        "it's a 'quoted' \"string\"",
        "-n",
        "--option=value",
        "~user",
        "#comment",
    };
    for (const auto &s : hostile) {
        int argc = 0;
        std::string got = roundTrip(s, &argc);
        expectEq(got, s, ("round trip of [" + s + "]").c_str());
        if (argc != 1) {
            std::fprintf(stderr, "FAIL round trip of [%s]: shell saw %d args, expected 1\n", s.c_str(), argc);
            ++failures;
        }
    }

    if (failures == 0) {
        std::printf("ShellQuoteTest: all %zu round trips passed\n", hostile.size());
        return 0;
    }
    std::fprintf(stderr, "ShellQuoteTest: %d failure(s)\n", failures);
    return 1;
}
