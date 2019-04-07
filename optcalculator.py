import os
import sys
import datetime
import copy
import QuantLib as ql

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def euromodel(price, underline, expire, strike, spot_vol, t):
    exercise = ql.EuropeanExercise(ql.Settings.instance().evaluationDate + expire)
    payoff = ql.PlainVanillaPayoff(t, strike)
    option = ql.EuropeanOption(payoff, exercise)

    underline = ql.QuoteHandle(ql.SimpleQuote(underline))
    dividend = ql.YieldTermStructureHandle(ql.FlatForward(0, ql.TARGET(), 0, ql.Actual365Fixed()))
    risk_free_rate = ql.YieldTermStructureHandle(ql.FlatForward(0, ql.TARGET(), 0.00, ql.Actual365Fixed()))
    spot_vol = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(0, ql.TARGET(), spot_vol, ql.Actual365Fixed()))

    process = ql.BlackScholesMertonProcess(underline, dividend, risk_free_rate, spot_vol)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))

    try:
        iv = option.impliedVolatility(price, process)
    except Exception as e:
        iv = 0

    fiv = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(0, ql.TARGET(), iv, ql.Actual365Fixed()))
    process = ql.BlackScholesMertonProcess(underline, dividend, risk_free_rate, fiv)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))

    delta = option.delta()
    vega = option.vega()
    gamma = option.gamma()
    theta = option.theta()

    return {
        "iv": iv,
        "delta": delta,
        "vega": vega,
        "gamma": gamma,
        "theta": theta
    }


def calculate_portfolio_greeks(opt_infos):
    total_greeks = {
        "delta": 0,
        "vega": 0,
        "gamma": 0,
        "theta": 0
    }

    for i in opt_infos:
        info = opt_infos[i]
        opt_g = euromodel(info["price"], info["underline"], info["expire"],
                          info["strike"], info["spot_vol"], info["type"])
        # print(opt_g)

        total_greeks["delta"] += opt_g["delta"]
        total_greeks["vega"] += opt_g["vega"]
        total_greeks["gamma"] += opt_g["gamma"]
        total_greeks["theta"] += opt_g["theta"]

    return total_greeks


def main():
    infos = {
        "opt1": {
            "price": 0.1034,
            "underline": 2.939,
            "expire": 17,
            "strike": 2.9,
            "spot_vol": 0.22,
            "type": ql.Option.Call
        },
        "opt2": {
            "price": 0.06,
            "underline": 2.939,
            "expire": 17,
            "strike": 2.9,
            "spot_vol": 0.22,
            "type": ql.Option.Put
        }
    }

    print(calculate_portfolio_greeks(infos))


if __name__ == '__main__':
    main()
