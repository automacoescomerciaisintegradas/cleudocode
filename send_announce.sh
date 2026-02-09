#!/bin/bash
curl -X POST http://144.91.118.78:8889/announce \
  -H "Content-Type: application/json" \
  -d '{"message": "Package delivered"}'
