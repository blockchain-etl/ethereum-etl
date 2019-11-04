class Chain:
    ETHEREUM = 'ethereum'

    @classmethod
    def ticker_symbol(cls, chain):
        symbols = {
            'ethereum': 'ETH',
        }
        return symbols.get(chain, None)

class CoinPriceType:

    empty = 0
    daily = 1
    hourly = 2
