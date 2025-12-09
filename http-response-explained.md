# Where Does the File Go? A Beginner's Guide

## The HTTP Request/Response Cycle

When you call your API endpoint, here's what happens:

```
Your Computer (Client)                    Server (FastAPI)
     |                                          |
     | 1. Send HTTP Request                     |
     |    GET /zonal_stats?...  ------------>  |
     |                                          |
     |                                          | 2. Server reads file from disk
     |                                          |    (zonal_stats2.fgb)
     |                                          |
     |                                          | 3. Server sends file in response
     |  <------------------------------------  |
     |    HTTP Response:                       |
     |    - Headers (metadata)                  |
     |    - Body (file bytes)                   |
     |                                          |
     | 4. Your computer receives it             |
     |    (stored in RAM temporarily)           |
     |                                          |
     | 5. You decide what to do with it         |
     |    - Save to disk?                       |
     |    - Display in browser?                 |
     |    - Process in code?                    |
```

## Step-by-Step: Where the Data Goes

### Step 1: Server Reads File
- Server has file on disk: `zonal_stats2.fgb`
- Server opens file and starts reading it

### Step 2: Server Sends Over Network
- File bytes travel over the network (WiFi/Ethernet)
- They're sent in small chunks (streaming)
- Like sending a book page by page through the mail

### Step 3: Your Computer Receives
- Bytes arrive at your computer's network card
- They go into your computer's **RAM (memory)** temporarily
- Think of RAM like a temporary holding area

### Step 4: Where It's Stored (Temporarily)
- In your web browser: stored in browser's memory
- In PowerShell: stored in `$response.Content` (in RAM)
- In JavaScript fetch: stored in the response object (in RAM)

### Step 5: You Decide What to Do
- **Browser**: Sees `Content-Disposition: attachment` → automatically saves to Downloads folder
- **PowerShell**: You must manually save it: `$response.Content` → write to disk
- **JavaScript**: You must manually save it: `response.blob()` → create download

## The Key Concept: RAM vs Disk

```
DISK (Permanent Storage)
├── zonal_stats2.fgb  (on server)
└── (empty on your computer initially)

RAM (Temporary Memory)
└── File bytes arrive here first (in $response.Content)

DISK (Permanent Storage)  
└── zonal_stats.fgb  (on your computer - AFTER you save it)
```

## Visual Example

Imagine the file is a book:

1. **Server has the book** (on disk: `zonal_stats2.fgb`)
2. **Server photocopies pages** and sends them to you (streaming over network)
3. **Pages arrive at your house** (your computer's RAM)
4. **You receive the pages** (stored in `$response.Content` in RAM)
5. **You decide**: 
   - Throw them away? (don't save - data lost when program ends)
   - Put them in a folder? (save to disk - permanent storage)

## In Your PowerShell Example

When you did:
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8000/zonal_stats?..."
```

Here's what happened:

1. Request sent to server
2. Server sent file bytes over network
3. Bytes arrived at your computer
4. PowerShell stored them in **RAM** in the variable `$response.Content`
5. The file is NOW in your computer's memory (RAM), but NOT on disk yet!

To put it on disk (permanent storage), you need to:
```powershell
[System.IO.File]::WriteAllBytes("zonal_stats.fgb", $response.Content)
```

This takes the bytes from RAM (`$response.Content`) and writes them to disk (`zonal_stats.fgb`).

## Summary

- **Streaming** = file bytes travel over network in chunks
- **Where it goes first** = your computer's RAM (memory)
- **Where it stays** = RAM only (temporary - lost when program closes)
- **To keep it permanently** = you must save it to disk

The file is "stored" in RAM when it arrives. You need to explicitly save it to disk if you want to keep it.


