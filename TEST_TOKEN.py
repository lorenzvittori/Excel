import dropbox

dbx = dropbox.Dropbox("IL_TUO_TOKEN")

print(dbx.users_get_current_account())