# ultrademark

Odoo addons vendored from
[`MARKDENNIS/hospital-management-emr`](https://github.com/MARKDENNIS/hospital-management-emr)
— release archive `realestate_website-19.0.1.0.0.zip` (master).

## Modules

| Module | Name | Version | Author | License |
| --- | --- | --- | --- | --- |
| `realestate_core` | Real Estate Core | 1.0.0 | Taqnix | LGPL-3 |
| `realestate_website` | Real Estate Website | 1.0.0 | Taqnix | LGPL-3 |
| `real_estate_management_pro` | Real Estate Management | 19.0.1.0.0 | Higa Solutions | LGPL-3 |
| `taqnix_app_builder` | Taqnix Mobile App Builder | 19.0.1.0.0 | Taqnix | OPL-1 |

The archive's top-level `realestate_website-19.0.1.0.0/` folder was flattened, so the
four modules sit at the repository root and can be dropped straight into an Odoo
addons path.

Install order follows the dependency chain:
`taqnix_app_builder` → `realestate_core` → `realestate_website`
(`real_estate_management_pro` is standalone: `base`, `mail`, `calendar`).
