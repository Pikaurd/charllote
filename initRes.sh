cp orient.sqlite3.db work.sqlite3.db
python3 Application.py --init
cp work.sqlite3.db dev.sqlite3.db
curl "http://share.popgo.org/rss/rss.xml" -o popgo.xml
echo "init finished"
