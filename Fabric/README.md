// // List of available models in fabric
// Ollama
llama3.2:1b
// Gemini
gemini-2.0-flash
gemini-1.5-flash
// ChatGPT
gpt-3.5-turbo
gpt-4

// youtube video summary extraction
fabric -y https://youtu.be/wPEyyigh10g?si=IsA6IxQb5RMP54oV > yt.txt
cat yt.txt | fabric -m gemini-2.0-flash -sp extract_wisdom | tee summary.md


fabric -m gemini-2.0-flash -s hi there // working

fabric -l | grep '^t_'
// get cmd related to the TALOS

cat telos.md | fabric -sp t_give_encouragement | tee telos_t_give_encouragement.md // streaming , pattern: t_give_encouragement, tee: show output and save to the .md file

fabric -y https://www.youtube.com/watch?v=UbDyjIIGaxQ
  632  yt-dlp --check-formats https://www.youtube.com/watch?v=UbDyjIIGaxQ
  633  yt-dlp --list-formats https://www.youtube.com/watch?v=UbDyjIIGaxQ
// youtube transcript not working

cat test02.txt | fabric -sp summarize | fabric -sp write_essay

 cat test01.txt | fabric -sp rate_content | tee rate_content.txt

// fabric patter.sh file, input parameter pattern_name,
// take input from Data/input.md and output to Data/timestamp_pattern_name.md
/home/ssbrpi/Project/Fabric/fabricPattern.sh <pattern_name>

