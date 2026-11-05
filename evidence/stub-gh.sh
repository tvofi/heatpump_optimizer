#!/bin/bash
printf '%s\x1f' "$@" >> "$STUBLOG"; printf '\n' >> "$STUBLOG"; exit 0
