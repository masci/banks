# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import warnings

# banks depends on modules producing loads of deprecation warnings, let's just ignore them,
# nothing we can do anyways
warnings.simplefilter("ignore", category=DeprecationWarning)
