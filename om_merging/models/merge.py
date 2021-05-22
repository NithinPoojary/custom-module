from odoo import fields, models, api, _
from openerp.exceptions import UserError

class MergeMove(models.TransientModel):
    _name = "merge.move"

    def merge_move(self):
        if self._context.get('active_model') == 'account.move':
            domain = [('id', 'in', self._context.get('active_ids', [])), ('state', '=', 'draft')]
            account_moves = self.env['account.move'].search(domain)
            print(account_moves)
            partner_ids = []
            for moves in account_moves:
                partner_ids.append(moves.partner_id.id)
            print(partner_ids)
            all_partner = all(partner == partner_ids[0] for partner in partner_ids)
            print(all_partner)
            if all_partner:
                print("action to be performed!")
                account_obj = self.env['account.move']
                vals = {
                    'currency_id': account_moves[0].currency_id,
                    'date': account_moves[0].date,
                    'move_type': account_moves[0].move_type,
                    'state': 'draft',
                    'company_id': self.env.company.id,
                    'partner_id': account_moves[0].partner_id.id,
                }
                line_val_lst = []
                for moves in account_moves:
                    for line in moves.invoice_line_ids:
                        line_vals = (0, 0, {
                            'move_id': line.move_id,
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'quantity': line.quantity,
                            'price_unit': line.price_unit,
                            'tax_ids': line.tax_ids,
                            'price_subtotal': line.price_subtotal
                        })
                        line_val_lst.append(line_vals)
                vals.update({
                    'invoice_line_ids': line_val_lst
                })
                new_invoice = account_obj.create(vals)
                print(new_invoice)
                print(account_moves)

                # Deleting Merged Invoices
                return account_moves.unlink()
                for line in account_moves:
                    return line.unlink()

            else:
                raise UserError(_("You have Selected invoices with different partners!"))


