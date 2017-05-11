#!/bin/bash

socat UDP4-RECVFROM:1234,broadcast,fork,crlf EXEC:"echo Recibido"