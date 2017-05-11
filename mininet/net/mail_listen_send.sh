#! /bin/sh

socat TCP4-LISTEN:2526,fork,reuseaddr EXEC:"echo 250 OK"