# todo
## main03.py
- add graph feature
- for ascii drawing
    - responce:
```
_______~~~~~~~~~~~~~~~
\             /
   ~~~~~~~~    ~~~~~~
  /        \      /
 /          \     /
|   __      |    |
 _| |_____ |_   _|
|       |       | |
|  __  |  __  | |
| |  | | |  | | |
| |__| | |__| | |
 \_________|_____/
         ~~~~~~~~
        /           \
       /             \
      /               \
     /                 \
    /                   \
   /                     \
  /                       \
    - Output:

  ```
  _______~~~~~~~~~~~~~~~
  \             /
  ~~~~~~~~    ~~~~~~
  /        \      /
  /          \     /
  |   __      |    |
  _| |_____ |_   _|
  |       |       | |
  |  __  |  __  | |
  | |  | | |  | | |
  | |__| | |__| | |
  \_________|_____/
  ~~~~~~~~
  /           \
  /             \
  /               \
  /                 \
  /                   \
  /                     \
  /                       \
  ```

## main05.py
- logs are not printign whole statement
- logs shuould be printing in streaming

# Ollama llm output comparator
## main02.py, 
- MODEL_NAME = "llama3.2:1b"                   # model name pulled in Ollama
- 5 stocks and its value wrt 100b$

```
```
────────────────────────────────────────────────────────────────────────

> 5 stocks and its value wrt 100b$

────────────────────────────────────────────────────────────────────────
  Assistant:
  ```bar CPU 43
  BAR Stock1,2500 | Stock2,1200 | Stock3,1800 | Stock4,2200 | Stock5,2400
  ```
  | **Stock Name** | **Current Value (B)** |
  | --- | --- |
  | Stock1 | 1250 |
  | Stock2 | 1200 |
  | Stock3 | 1800 |
  | Stock4 | 2200 |
  | Stock5 | 2400 |
  ```
  --------------
  Planet   Moons
  --------------
  Earth    1    
  Mars     2    
  Jupiter  95   
  --------------
  ```
  **Planets in our Solar System**
  * **Mercury**: 1 Moon
  * **Earth**: 1
  * **Mars**: 2
  * **Jupiter**: 95
  ```
  BOX Status System is healthy
  ```
────────────────────────────────────────────────────────────────────────
```
```

2026-06-06 20:55:39  INFO      ==================== OLLAMA REQUE
ST ====================
{
  "model": "llama3.2:1b",
  "stream": true,
  "messages": [
    {
      "role": "system",
      "content": "You are an AI terminal assistant running on a 
Raspberry Pi.\nRespond concisely. When it makes sense, enrich yo
ur response with the\nfollowing special tags so the terminal ren
derer can draw live UI components:\n\n  [BAR <label> <0-100>]\n 
     Draws a labelled progress bar.\n      Example: [BAR CPU 43]
\n\n  [TABLE <col1>,<col2>,... | <r1c1>,<r1c2>,... | <r2c1>,<r2c
2>,...]\n      Draws an ASCII table. Columns separated by comma,
 rows separated by |\n      Example: [TABLE Planet,Moons | Earth
,1 | Mars,2 | Jupiter,95]\n\n  [BOX <title> <single-line content
>]\n      Draws a boxed panel with a title.\n      Example: [BOX
 Status System is healthy]\n\nYou may mix plain text and tags fr
eely. Each tag must be on its own line.\nKeep responses short an
d practical."
    },
    {
      "role": "user",
      "content": "5 stocks and its value wrt 100b$"
    }
  ]
}
2026-06-06 20:55:39  INFO      ==================== OLLAMA RESPO
NSE ===================
```bar CPU 43
BAR Stock1,2500 | Stock2,1200 | Stock3,1800 | Stock4,2200 | Stoc
k5,2400
```

| **Stock Name** | **Current Value (B)** |
| --- | --- |
| Stock1 | 1250 |
| Stock2 | 1200 |
| Stock3 | 1800 |
| Stock4 | 2200 |
| Stock5 | 2400 |

```
[TABLE Planet,Moons | Earth,1 | Mars,2 | Jupiter,95]
```

**Planets in our Solar System**

* **Mercury**: 1 Moon
* **Earth**: 1
* **Mars**: 2
* **Jupiter**: 95

```
BOX Status System is healthy
```
2026-06-06 20:55:39  INFO      
==================== LLM STATS ====================
Prompt Tokens      : 238
Completion Tokens  : 170
Total Tokens       : 408
Prompt Time        : 0.151 sec
Generation Time    : 33.122 sec
Load Time          : 0.303 sec
Total Time         : 33.757 sec
Prompt Speed       : 1574.56 tok/s
Generation Speed   : 5.13 tok/s
===================================================
2026-06-06 20:55:39  INFO      OllamaAPI   | response complete  
tokens_received=169


- MODEL_NAME = "llama3.2"                   # model name pulled in Ollama
2026-06-06 21:00:05  INFO      ==================== OLLAMA REQUE
ST ====================
{
  "model": "llama3.2",
  "stream": true,
  "messages": [
    {
      "role": "system",
      "content": "You are an AI terminal assistant running on a 
Raspberry Pi.\nRespond concisely. When it makes sense, enrich yo
ur response with the\nfollowing special tags so the terminal ren
derer can draw live UI components:\n\n  [BAR <label> <0-100>]\n 
     Draws a labelled progress bar.\n      Example: [BAR CPU 43]
\n\n  [TABLE <col1>,<col2>,... | <r1c1>,<r1c2>,... | <r2c1>,<r2c
2>,...]\n      Draws an ASCII table. Columns separated by comma,
 rows separated by |\n      Example: [TABLE Planet,Moons | Earth
,1 | Mars,2 | Jupiter,95]\n\n  [BOX <title> <single-line content
>]\n      Draws a boxed panel with a title.\n      Example: [BOX
 Status System is healthy]\n\nYou may mix plain text and tags fr
eely. Each tag must be on its own line.\nKeep responses short an
d practical."
    },
    {
      "role": "user",
      "content": "5 stocks and its value wrt 100b$"
    }
  ]
}
2026-06-06 21:00:05  INFO      ==================== OLLAMA RESPO
NSE ===================
[BOX Stock Details]
[BAR Market Value | 85,210,000]
2026-06-06 21:00:05  INFO      
==================== LLM STATS ====================
Prompt Tokens      : 238
Completion Tokens  : 18
Total Tokens       : 256
Prompt Time        : 28.712 sec
Generation Time    : 3.915 sec
Load Time          : 27.322 sec
Total Time         : 59.971 sec
Prompt Speed       : 8.29 tok/s
Generation Speed   : 4.60 tok/s
===================================================
2026-06-06 21:00:05  INFO      OllamaAPI   | response complete  
tokens_received=17

> 5 stocks and its value wrt 100b$

────────────────────────────────────────────────────────────────────────
  Assistant:
  ┌──────────────────────────────────────────────────────────────────────┐
  │                                Stock                                 │
  ├──────────────────────────────────────────────────────────────────────┤
  │ Details                                                              │
  └──────────────────────────────────────────────────────────────────────┘
  [BAR Market Value | 85,210,000]
────────────────────────────────────────────────────────────────────────

- MODEL_NAME = "llama2-uncensored:7b"                   # model name pulled in Ollama
────────────────────────────────────────────────────────────────────────

> 5 stocks and its value wrt 100b$

────────────────────────────────────────────────────────────────────────
  Assistant:
  -------------
  Stock1  Price
  -------------
  Stock2  Price
  Stock3  Price
  Stock4  Price
  Stock5  Price
  -------------
────────────────────────────────────────────────────────────────────────

>  

2026-06-06 21:30:58  INFO      ==================== OLLAMA REQUE
ST ====================
{
  "model": "llama2-uncensored:7b",
  "stream": true,
  "messages": [
    {
      "role": "system",
      "content": "You are an AI terminal assistant running on a 
Raspberry Pi.\nRespond concisely. When it makes sense, enrich yo
ur response with the\nfollowing special tags so the terminal ren
derer can draw live UI components:\n\n  [BAR <label> <0-100>]\n 
     Draws a labelled progress bar.\n      Example: [BAR CPU 43]
\n\n  [TABLE <col1>,<col2>,... | <r1c1>,<r1c2>,... | <r2c1>,<r2c
2>,...]\n      Draws an ASCII table. Columns separated by comma,
 rows separated by |\n      Example: [TABLE Planet,Moons | Earth
,1 | Mars,2 | Jupiter,95]\n\n  [BOX <title> <single-line content
>]\n      Draws a boxed panel with a title.\n      Example: [BOX
 Status System is healthy]\n\nYou may mix plain text and tags fr
eely. Each tag must be on its own line.\nKeep responses short an
d practical."
    },
    {
      "role": "user",
      "content": "5 stocks and its value wrt 100b$"
    }
  ]
}
2026-06-06 21:30:58  INFO      ==================== OLLAMA RESPO
NSE ===================
[TABLE Stock1,Price | Stock2,Price | Stock3,Price | Stock4,Price
 | Stock5,Price]

2026-06-06 21:30:58  INFO      
==================== LLM STATS ====================
Prompt Tokens      : 277
Completion Tokens  : 29
Total Tokens       : 306
Prompt Time        : 6.333 sec
Generation Time    : 11.998 sec
Load Time          : 0.033 sec
Total Time         : 18.377 sec
Prompt Speed       : 43.74 tok/s
Generation Speed   : 2.42 tok/s
===================================================
2026-06-06 21:30:58  INFO      OllamaAPI   | response complete  
tokens_received=28
j  


# run ollama as docker image
sudo docker rm -f ollama

sudo docker run -d \
  --name ollama \
  -p 11434:11434 \
  -e OLLAMA_MAX_LOADED_MODELS=1 \
  -v ollama:/root/.ollama \
  alpine/ollama

python main.py

docker ps

docker logs -f ollama

curl http://localhost:11434

tail -f log-.log
tail -f 

docker exec -it ollama sh


# Temp
| Component         | Example                                                    |
| ----------------- | ---------------------------------------------------------- |
| Progress Bar      | `[BAR Download 67]`                                        |
| Table             | `[TABLE Name,Age \| Alice,20 \| Bob,25]`                   |
| Box               | `[BOX Status All systems operational]`                     |
| Spinner           | `[SPINNER Thinking]`                                       |
| Badge             | `[BADGE SUCCESS Connected]`                                |
| Alert             | `[ALERT WARNING Battery Low]`                              |
| Divider           | `[DIVIDER System Info]`                                    |
| Tree              | `[TREE root -> src -> main.py]`                            |
| List              | `[LIST Apple \| Banana \| Orange]`                         |
| Checklist         | `[CHECKLIST x Install Docker \| o Configure Ollama]`       |
| Timeline          | `[TIMELINE 10:00 Boot \| 10:01 Load Model \| 10:02 Ready]` |
| Code              | `[CODE python print("Hello")]`                             |
| Quote             | `[QUOTE Knowledge is power.]`                              |
| Stats             | `[STATS CPU=32 RAM=48 TEMP=61]`                            |
| Gauge             | `[GAUGE Speed 78]`                                         |
| Sparkline         | `[SPARKLINE 1,3,5,4,6,8,7]`                                |
| Chart             | `[CHART 10,20,30,15,40]`                                   |
| Pie               | `[PIE Linux=70 Windows=20 Mac=10]`                         |
| Calendar          | `[CALENDAR 2026-06]`                                       |
| Clock             | `[CLOCK 22:31:14]`                                         |
| Countdown         | `[COUNTDOWN 15]`                                           |
| Tabs              | `[TABS Logs,Stats,System ACTIVE=Stats]`                    |
| Accordion         | `[SECTION Network expanded]`                               |
| Menu              | `[MENU Home,Settings,Exit]`                                |
| Cards             | `[CARD CPU Usage 43%]`                                     |
| Grid              | `[GRID 2x2 A,B,C,D]`                                       |
| Avatar            | `[AVATAR Robot]`                                           |
| Image             | `[IMAGE ./logo.png]`                                       |
| SVG               | `[SVG ./diagram.svg]`                                      |
| Markdown          | `[MARKDOWN ## Title]`                                      |
| File Tree         | `[FILETREE src/main.py,src/ui.py,README.md]`               |
| Terminal Output   | `[TERMINAL ls -la]`                                        |
| Log               | `[LOG INFO Server started]`                                |
| Notification      | `[NOTIFY Download Complete]`                               |
| Toast             | `[TOAST Saved successfully]`                               |
| Chat Bubble       | `[CHAT USER Hello]`                                        |
| Bubble            | `[BUBBLE AI Processing...]`                                |
| Status Dot        | `[STATUS GREEN Connected]`                                 |
| Tags              | `[TAGS Python,Docker,AI]`                                  |
| Keyboard Shortcut | `[KEY Ctrl+C Interrupt]`                                   |
| Metric            | `[METRIC FPS 58]`                                          |
| Histogram         | `[HIST 3,5,8,2,6]`                                         |
| Heatmap           | `[HEATMAP 1,2,5;3,4,1]`                                    |
| Radar             | `[RADAR Speed=8 Memory=5 CPU=9]`                           |
| Network Graph     | `[GRAPH A-B,B-C,C-D]`                                      |
| Dependency Graph  | `[DAG App->API->DB]`                                       |
| JSON Viewer       | `[JSON {"cpu":42}]`                                        |
| YAML Viewer       | `[YAML cpu:42]`                                            |
| Diff              | `[DIFF -old +new]`                                         |
| Tabs with Content | `[TAB System ...ENDTAB]`                                   |
| Collapsible       | `[COLLAPSE Logs hidden]`                                   |
| Progress Steps    | `[STEPS Build>Test>Deploy CURRENT=Test]`                   |
| Kanban            | `[KANBAN Todo:2 Doing:1 Done:5]`                           |
| Leaderboard       | `[LEADER Alice=95 Bob=87]`                                 |
| Scoreboard        | `[SCORE TeamA=120 TeamB=118]`                              |
| Map               | `[MAP India:Pune]`                                         |
| Mini Dashboard    | `[DASH CPU=20 RAM=45 NET=12 DISK=67]`                      |
| Loading Skeleton  | `[SKELETON table]`                                         |
| QR Code           | `[QRCODE https://example.com]`                             |
| Emoji Meter       | `[EMOJI 😊😊😊😐😐]`                                       |
| Stopwatch         | `[STOPWATCH 00:01:25]`                                     |

