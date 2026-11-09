import uuid
import time

class B2BFulfillmentEngine:
    def __init__(self, initial_wallet_balance_sar: float = 50000.0):
        self.wallet_balance_sar = initial_wallet_balance_sar
        self.bookings = {}

    def get_wallet_status(self) -> dict:
        return {
            "currency": "SAR",
            "available_credit": self.wallet_balance_sar,
            "status": "HEALTHY" if self.wallet_balance_sar >= 5000.0 else "LOW_BALANCE_WARNING"
        }

    def create_reservation(self, origin: str, destination: str, date: str, net_fare_sar: float, passenger: dict) -> dict:
        if self.wallet_balance_sar < net_fare_sar:
            return {
                "success": False,
                "error": "INSUFFICIENT_B2B_WALLET_FUNDS",
                "available": self.wallet_balance_sar,
                "required": net_fare_sar
            }

        pnr = "".join(uuid.uuid4().hex[:6].upper())
        reservation = {
            "pnr": pnr,
            "origin": origin,
            "destination": destination,
            "departure_date": date,
            "passenger": passenger,
            "net_fare_sar": net_fare_sar,
            "status": "HELD",
            "created_at": time.time()
        }
        self.bookings[pnr] = reservation
        return {
            "success": True,
            "pnr": pnr,
            "status": "HELD",
            "net_fare_sar": net_fare_sar,
            "expires_in_minutes": 30
        }

    def issue_ticket(self, pnr: str) -> dict:
        if pnr not in self.bookings:
            return {"success": False, "error": "PNR_NOT_FOUND"}

        res = self.bookings[pnr]
        if res["status"] == "ISSUED":
            return {"success": True, "pnr": pnr, "status": "ALREADY_ISSUED", "ticket_number": res.get("ticket_number")}

        fare = res["net_fare_sar"]
        self.wallet_balance_sar -= fare
        tkt_no = f"065-{int(time.time()*1000)%10000000000:010d}"
        res["status"] = "ISSUED"
        res["ticket_number"] = tkt_no

        return {
            "success": True,
            "pnr": pnr,
            "ticket_number": tkt_no,
            "deducted_sar": fare,
            "remaining_wallet_balance_sar": self.wallet_balance_sar,
            "status": "CONFIRMED_AND_ISSUED"
        }

fulfillment_engine = B2BFulfillmentEngine()
