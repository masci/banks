# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from banks.extensions.generate import GenerateExtension
from banks.extensions.inference_endpoint import HFInferenceEndpointsExtension

__all__ = ("GenerateExtension", "HFInferenceEndpointsExtension")
