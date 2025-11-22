#!/bin/bash
mkdir -p public/static
cp -r static/* public/static/ 2>/dev/null || true
cp -r templates/* public/ 2>/dev/null || true
