import json

import numpy as np
import pandas as pd


class PLCalculator:
    def __init__(self, input: pd.DataFrame):
        self.input = input

    def signed_amount(self):
        self.input["amount_signed"] = self.input.apply(
            lambda row: row["amount"] if row["side"] == 1 else -row["amount"], axis=1
        )
        return self.input

    def running_balance(self):
        self.input["running_balance"] = (
            self.input[["instrument_exch", "amount_signed"]]
            .groupby("instrument_exch")
            .cumsum()
        )
        return self.input

    def lag_running_balance(self):
        self.input["lag_running_balance"] = self.input.groupby("instrument_exch")[
            "running_balance"
        ].shift(1)
        return self.input

    @staticmethod
    def _amount_liquidated(row):
        if np.sign(row["amount_signed"]) * np.sign(row["lag_running_balance"]) == -1:
            return min(abs(row["amount_signed"]), abs(row["lag_running_balance"]))
        else:
            return 0

    @staticmethod
    def _liquidation_check(row):
        if np.sign(row["amount_signed"]) * np.sign(row["running_balance"]) == -1:
            return int(1)
        else:
            return int(0)

    @staticmethod
    def _liquidation_check_group(group: pd.DataFrame):
        df = group.apply(lambda row: PLCalculator._liquidation_check(row), axis=1)
        return df

    def amount_liquidated(self):
        self.input["amount_liquidated"] = self.input.apply(
            lambda row: self._amount_liquidated(row), axis=1
        )
        return self.input

    def flags_calc(self):
        for name, group in self.input.groupby("instrument_exch"):
            self.input.loc[
                group.index, "flag_liquidation"
            ] = self._liquidation_check_group(group)
        self.input["flag_liquidation"] = self.input["flag_liquidation"].astype(int)
        return self.input

    def inventory_metrics(self):
        input_data = self.input.groupby("instrument_exch")
        for name, group in input_data:
            running_inventory = 0
            inventory_cost = 0
            for index, row in group.iterrows():
                if row["lag_running_balance"] == 0 or row["amount_liquidated"] > 0:
                    inventory_change = (
                        row["price"]
                        * row["running_balance"]
                        * (1 - row["flag_liquidation"])
                    )
                else:
                    inventory_change = (
                        row["amount_signed"]
                        * row["price"]
                        * (1 - row["flag_liquidation"])
                    )
                inventory_change += (
                    row["side"] * row["amount_liquidated"] * inventory_cost
                )
                running_inventory += inventory_change
                inventory_cost = running_inventory / row["running_balance"]
                self.input.loc[index, "inventory_change"] = inventory_change
                self.input.loc[index, "running_inventory"] = running_inventory
                self.input.loc[index, "inventory_cost"] = inventory_cost
        return self.input

    @staticmethod
    def _realized_pnl(row):
        price_diff = (
            -1 * row["side"] * row["price"]
            - 1 * np.sign(row["lag_running_inventory"]) * row["lag_inventory_cost"]
        )
        return row["amount_liquidated"] * price_diff

    @staticmethod
    def _unrealized_pnl(row):
        price_diff = row["price"] - row["lag_inventory_cost"]
        sign = np.sign(row["lag_running_inventory"])
        return price_diff * row["running_balance"] * sign

    @staticmethod
    def _convert_to_usd(row, col_name: str):
        if row["cur_quote"] == "USD":
            return row[col_name]
        elif row["cur_base"] == "USD":
            return row[col_name] / row["price"]
        else:
            raise ValueError("Neither quote nor base currency is USD")

    def pnl_calc(self):
        self.input["lag_running_inventory"] = self.input.groupby("instrument_exch")[
            "running_inventory"
        ].shift(1)
        self.input["lag_inventory_cost"] = self.input.groupby("instrument_exch")[
            "inventory_cost"
        ].shift(1)
        self.input["realized_pnl_quote_currency"] = self.input.apply(
            lambda row: self._realized_pnl(row), axis=1
        )
        self.input["unrealized_pnl_quote_currency"] = self.input.apply(
            lambda row: self._unrealized_pnl(row), axis=1
        )

        self.input["realized_pnl_usd"] = self.input.apply(
            lambda row: self._convert_to_usd(row, "realized_pnl_quote_currency"), axis=1
        )
        self.input["unrealized_pnl_usd"] = self.input.apply(
            lambda row: self._convert_to_usd(row, "unrealized_pnl_quote_currency"),
            axis=1,
        )

        self.input.drop(
            ["lag_running_inventory", "lag_inventory_cost"], axis=1, inplace=True
        )

        return self.input

    def calculate_totals(self):
        groups = self.input.groupby("instrument_exch")
        total_metrics = {}
        for name, group in groups:
            unrealized_pnl = group["unrealized_pnl_usd"].iloc[-1]
            realized_pnl = group["realized_pnl_usd"].sum()
            total_pnl = unrealized_pnl + realized_pnl
            total_metrics[name] = {
                "unrealized_pnl": unrealized_pnl,
                "realized_pnl": realized_pnl,
                "total_pnl": total_pnl,
            }
        with open("total_metrics.json", "w") as f:
            json.dump(total_metrics, f)

    def calculate(self):
        self.signed_amount()
        self.running_balance()
        self.lag_running_balance()
        self.amount_liquidated()
        self.flags_calc()
        self.inventory_metrics()
        self.pnl_calc()
        return self.input
