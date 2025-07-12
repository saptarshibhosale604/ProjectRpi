fabric -l | grep '^t_'
// get cmd related to the TALOS

cat telos.md | fabric -sp t_give_encouragement | tee telos_t_give_encouragement.md // streaming , pattern: t_give_encouragement, tee: show output and save to the .md file

fabric -y https://www.youtube.com/watch?v=UbDyjIIGaxQ
  632  yt-dlp --check-formats https://www.youtube.com/watch?v=UbDyjIIGaxQ
  633  yt-dlp --list-formats https://www.youtube.com/watch?v=UbDyjIIGaxQ
// youtube transcript not working

cat test02.txt | fabric -sp summarize | fabric -sp write_essay

 cat test01.txt | fabric -sp rate_content | tee rate_content.txt
