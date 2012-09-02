# Backs up the database to the backups folder.
n=1
_NEXT_FILE="backups/convos_$n.sql"
while [ -f "$_NEXT_FILE" ]
  do
    n=$(( ${n:-0} + 1 ))
   _NEXT_FILE="backups/convos_$n.sql"
done
echo "Backing up to $_NEXT_FILE"

mysqldump -pconvos convos > $_NEXT_FILE