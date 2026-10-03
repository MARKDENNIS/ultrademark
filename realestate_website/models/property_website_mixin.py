from odoo import api, fields, models

class RealEstatePropertyWebsite(models.Model):
    _inherit = 'estate.property'



    def _format_compact_amount(self, amount, currency=None, digits=1):
        """Return e.g. '$1.2M' or 'AED 950K' respecting currency symbol & position."""
        currency = currency or getattr(self, 'currency_id', False)
        if amount is None:
            amount = 0.0
        n = float(amount)
        absn = abs(n)

        if absn >= 1_000_000_000_000:
            val, suf = n / 1_000_000_000_000, 'T'
        elif absn >= 1_000_000_000:
            val, suf = n / 1_000_000_000, 'B'
        elif absn >= 1_000_000:
            val, suf = n / 1_000_000, 'M'
        elif absn >= 1_000:
            val, suf = n / 1_000, 'K'
        else:
            val, suf = n, ''

        fmt = f"{val:.{digits}f}".rstrip('0').rstrip('.')
        text = f"{fmt}{suf}"

        if currency:
            sym = currency.symbol or currency.name or ''
            if currency.position == 'before':
                return f"{sym} {text}".strip()
            return f"{text} {sym}".strip()
        return text

    def _format_compact_price(self):
        self.ensure_one()
        return self._format_compact_amount(self.price, self.currency_id)

    def _format_compact_rent(self):
        self.ensure_one()
        return self._format_compact_amount(getattr(self, 'rent_price', 0.0), self.currency_id)

