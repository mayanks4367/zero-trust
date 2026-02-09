savedcmd_vault_driver.mod := printf '%s\n'   vault_driver.o | awk '!x[$$0]++ { print("./"$$0) }' > vault_driver.mod
