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
#pragma once

#include <string>

namespace autil {

// Quote `str` as exactly one POSIX shell word.
//
// The result is wrapped in single quotes; inside single quotes the shell
// interprets nothing, so the only character needing care is the single quote
// itself, which is emitted as '\'' (close quote, escaped quote, reopen quote).
// Use this for every value interpolated into a command run via system() or
// popen(). Dependency-free so it can be used from headers such as Backtrace.h
// and unit-tested in isolation.
inline std::string shellQuote(const std::string &str) {
    std::string quoted;
    quoted.reserve(str.size() + 2);
    quoted += '\'';
    for (char c : str) {
        if (c == '\'') {
            quoted += "'\\''";
        } else {
            quoted += c;
        }
    }
    quoted += '\'';
    return quoted;
}

} // namespace autil
