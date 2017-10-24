#!/usr/bin/python
# -*- coding: UTF-8 -*-

import httplib
import json
from time import sleep

# Copyright (c) 2017 The Karbowanec developers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class SimpleWallet:

  service_host = ''
  service_port = 0
  socket_status = False
  api_status = False
  service_host_default = '127.0.0.1'
  service_port_default = 15000
  rpc_v = '2.0'
  id_conn = 'EWF8aIFX0y9w'
  decimal_point = 12
  prec_point = 4
  fee = 0.0001
  mixin = 0

  def __init__(self, host = '', port = 0):
    if (host != ''):
      self.service_host = host
    else:
      self.service_host = self.service_host_default
    if (port != 0):
      self.service_port = port
    else:
      self.service_port = self.service_port_default

  def AmountFormat(self, amount, mode):
    res = None
    if (mode):
      res = long(round(amount * pow(10, self.decimal_point), 0))
    else:
      res = 0.0
      if (amount > 0):
        res = float(round(amount / float(pow(10, self.decimal_point)), self.prec_point))
    return res

  def client(self, data):
    buff = ''
    self.socket_status = False
    try:
      conn = httplib.HTTPConnection(self.service_host, self.service_port, timeout=10);
      headers = {'Content-Type': 'application/json; charset=utf-8'}
      sleep(0.05)
      conn.request('POST', '/json_rpc', json.dumps(data), headers)
      res = conn.getresponse()
      if (res.status == 200):
        buff = res.read()
        #print(buff)
        self.socket_status = True
        conn.close()
    except:
      self.socket_status = False
    return buff;

  def doReset(self):
    self.api_status = False
    args = {'jsonrpc': self.rpc_v, 'id' : self.id_conn, 'method': 'reset'}
    res = self.client(args)
    if (self.socket_status):
      try:
        json_obj = json.loads(res)
        err_t = False
        if ('error' in json_obj):
          err_t = True
        if ('id' in json_obj):
          if (err_t == False and json_obj['id'] == self.id_conn):
            self.api_status = True
      except:
        self.api_status = False

  def getHeight(self):
    self.api_status = False
    args = {'jsonrpc': self.rpc_v, 'id' : self.id_conn, 'method': 'get_height'}
    res = self.client(args)
    height = 0
    if (self.socket_status):
      try:
        json_obj = json.loads(res)
        err_t = False
        if ('error' in json_obj):
          err_t = True
        if ('id' in json_obj):
          if (err_t == False and json_obj['id'] == self.id_conn):
            if ('result' in json_obj):
              res_obj = json_obj['result']
              if ('height' in res_obj):
                height = int(res_obj['height'])
            self.api_status = True
      except:
        self.api_status = False
    result = {'height': height}
    return result

  def getBalance(self):
    self.api_status = False
    args = {'jsonrpc': self.rpc_v, 'id' : self.id_conn, 'method': 'getbalance'}
    res = self.client(args)
    available_balance = 0.0
    locked_amount = 0.0
    if (self.socket_status):
      try:
        json_obj = json.loads(res)
        err_t = False
        if ('error' in json_obj):
          err_t = True
        if ('id' in json_obj):
          if (err_t == False and json_obj['id'] == self.id_conn):
            if ('result' in json_obj):
              res_obj = json_obj['result']
              if ('available_balance' in res_obj):
                available_balance = self.AmountFormat(long(res_obj['available_balance']), False)
              if ('locked_amount' in res_obj):
                locked_amount = self.AmountFormat(long(res_obj['locked_amount']), False)
            self.api_status = True
      except:
        self.api_status = False
    result = {'available_balance': available_balance, 'locked_amount': locked_amount}
    return result

  def doTransfer(self, destinations_in, payment_id = ''):
    self.api_status = False
    destinations = []
    for destination in destinations_in:
      destinations.append({'address': destination['address'], 'amount': self.AmountFormat(float(destination['amount']), True)})
    tx_fee = self.AmountFormat(self.fee, True)
    params = {'destinations': destinations, 'fee': tx_fee, 'mixin': self.mixin, 'unlock_time': 0, 'payment_id': payment_id}
    args = {'jsonrpc': self.rpc_v, 'id' : self.id_conn, 'method': 'transfer', 'params': params}
    #print(json.dumps(args))
    res = self.client(args)
    tx_hash = ''
    if (self.socket_status):
      try:
        json_obj = json.loads(res)
        err_t = False
        if ('error' in json_obj):
          err_t = True
        if ('id' in json_obj):
          if (err_t == False and json_obj['id'] == self.id_conn):
            if ('result' in json_obj):
              res_obj = json_obj['result']
              if ('tx_hash' in res_obj):
                tx_hash = str(res_obj['tx_hash'])
            self.api_status = True
      except:
        self.api_status = False
    result = {'tx_hash': tx_hash}
    return result

  def getTransfers(self):
    self.api_status = False
    args = {'jsonrpc': self.rpc_v, 'id' : self.id_conn, 'method': 'get_transfers'}
    res = self.client(args)
    result = []
    if (self.socket_status):
      try:
        json_obj = json.loads(res)
        err_t = False
        if ('error' in json_obj):
          err_t = True
        if ('id' in json_obj):
          if (err_t == False and json_obj['id'] == self.id_conn):
            if ('result' in json_obj):
              res_obj = json_obj['result']
              if ('transfers' in res_obj):
                transfers = res_obj['transfers']
                if (len(transfers) > 0):
                  for transfer in transfers:
                    address = ''
                    if 'address' in transfer:
                      address = str(transfer['address'])
                    amount = 0.0
                    if 'amount' in transfer:
                      amount = self.AmountFormat(long(transfer['amount']), False)
                    blockIndex = 0
                    if 'blockIndex' in transfer:
                      blockIndex = int(transfer['blockIndex'])
                    fee = 0.0
                    if 'fee' in transfer:
                      fee = self.AmountFormat(long(transfer['fee']), False)
                    output = False
                    if 'output' in transfer:
                      output = bool(transfer['output'])
                    paymentId = ''
                    if 'paymentId' in transfer:
                      paymentId = str(transfer['paymentId'])
                    time = 0
                    if 'time' in transfer:
                      time = int(transfer['time'])
                    transactionHash = ''
                    if 'transactionHash' in transfer:
                      transactionHash = str(transfer['transactionHash'])
                    unlockTime = 0
                    if 'unlockTime' in transfer:
                      unlockTime = int(transfer['unlockTime'])
                    result.append({'address': address,
                                   'amount': amount,
                                   'blockIndex': blockIndex,
                                   'fee': fee,
                                   'output': output,
                                   'paymentId': paymentId,
                                   'time': time,
                                   'transactionHash': transactionHash,
                                   'unlockTime': unlockTime
                                  })
            self.api_status = True
      except:
        self.api_status = False
    return result

  def getStatus(self):
    return self.api_status
  