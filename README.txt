curl -X POST \
  'https://fiupxaqbybacdojwztar.supabase.co/functions/v1/articles-insert' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpdXB4YXFieWJhY2Rvand6dGFyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTcwOTQwMCwiZXhwIjoyMDc3Mjg1NDAwfQ.Qs7vSHR5fuaKS1gDu8HXS9DcUvNMVBDr9lVenlSEBkw' \
  -d @payload.json

{"data":{"id":20,"created_at":"2025-11-05T18:07:43.650569+00:00","feed_url":"https://example.com/rss","title":"Inserted from CLI","url":"https://example.com/article","author":"CLI tester","published":"2025-11-05","description":"posted from curl","summary":"summary here","category":"news","category_scores":{"news":0.9}}}%


curl -L -X GET 'https://fiupxaqbybacdojwztar.supabase.co/functions/v1/articles-get-api'  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpdXB4YXFieWJhY2Rvand6dGFyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTcwOTQwMCwiZXhwIjoyMDc3Mjg1NDAwfQ.Qs7vSHR5fuaKS1gDu8HXS9DcUvNMVBDr9lVenlSEBkw'
[{"id":1,"title":"'This summer was chaotic': the Balearic Islands face an unprecedented number of migrants","published":"2025-10-29","created_at":"2025-10-29T13:05:04.220367+00:00"},{"id":2,"title":"Italy: Foreign logistics workers 'exploited' says CGIL union","published":"2025-10-29","created_at":"2025-10-29T13:05:06.045799+00:00"},
  {"id":3,"title":"Libya: 18 dead in capsized migrant boat accident","published":"2025-10-29","created_at":"2025-10-29T13:05:08.184773+00:00"},{"id":4,"title":"Immigration a key topic in 2025 Netherlands election","published":"2025-10-29","created_at":"2025-10-29T13:05:10.586772+00:00"},{"id":5,"title":"Germany: Police officer guilty of not pursuing future killer","published":"2025-10-29","created_at":"2025-10-29T13:05:13.188811+00:00"},
  {"id":6,"title":"UK wasted billions on asylum accommodation, MPs argue in report","published":"2025-10-28","created_at":"2025-10-29T13:05:16.399453+00:00"},{"id":7,"title":"UK: Defense Ministry data breach could have led to the deaths of at least 49 Afghans","published":"2025-10-28","created_at":"2025-10-29T13:05:18.487859+00:00"},
  {"id":8,"title":"Czechia: Ukrainian refugees fear new government's policies","published":"2025-10-28","created_at":"2025-10-29T13:05:20.453551+00:00"},{"id":9,"title":"Italy: Work to build Trento repatriation center 'set to start in 2026'","published":"2025-10-28","created_at":"2025-10-29T13:05:22.632878+00:00"},
  {"id":10,"title":"'Not our problem…ask the Italians': Albanian PM Edi Rama says of Italian migrant hubs","published":"2025-10-28","created_at":"2025-10-29T13:05:25.147438+00:00"}]%