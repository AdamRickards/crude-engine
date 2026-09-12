# offline_gold fixtures (#165)

Sanitized sample config + schema-shaped gold floors for
`tests/offline_gold_matrix.py`. No device hostnames, IPs.

For a fuller local prove against a bag NVM export (gitignored / outside
this tree), pass `--config` to a local `config_nvm_config.xml` and a
matching `--gold` JSON. Do not commit bag or device identity.

`catalogue_inventory_draft.md` is the #169 first-pass method catalogue
(no identity). Classes are heuristics until floored receipts refine them.
