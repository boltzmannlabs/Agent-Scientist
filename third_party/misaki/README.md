# Bundled Misaki source

This directory contains Misaki 0.9.4's official Python source and data, by
hexgrad, under its original Apache-2.0 license. SCI changes only the package's
Python upper bound from 3.13 to 3.15, matching the compatibility adjustment
previously required by the optional KittenTTS dependency. G2P algorithms and data
are unchanged. No upstream fork is downloaded during dependency installation.

Source: https://pypi.org/project/misaki/0.9.4/

Official source archive SHA256:
`3960fa3e6de179a90ee8e628446a4a4f6b8c730b6e3410999cf396189f4d9c40`.

The source archive's development lockfile, funding metadata, examples and build
metadata are not needed by SCI and are excluded. Keep LICENSE and the source
attribution when redistributing. Runtime speech models and optional dependencies
are installed only when their corresponding voice provider is selected.
