# How to Download Files from FileResponse Endpoints

## Using curl

### Option 1: curl automatically saves (easiest)
```bash
curl -O -J "http://localhost:8000/zonal_stats?polygon_url=...&raster_url=..."
```
- `-O` saves file with remote filename
- `-J` uses filename from `Content-Disposition` header
- File saved as `zonal_stats.fgb` in current directory

### Option 2: curl with custom filename
```bash
curl "http://localhost:8000/zonal_stats?polygon_url=...&raster_url=..." -o my_file.fgb
```
- `-o` specifies output filename
- Saves body bytes to `my_file.fgb`

### Option 3: curl to see what you get
```bash
# See headers
curl -I "http://localhost:8000/zonal_stats?polygon_url=...&raster_url=..."

# See body (first 100 bytes)
curl "http://localhost:8000/zonal_stats?polygon_url=...&raster_url=..." | head -c 100

# Save body to file
curl "http://localhost:8000/zonal_stats?polygon_url=...&raster_url=..." > output.fgb
```

## Using JavaScript fetch

### Option 1: Trigger browser download
```javascript
fetch('/zonal_stats?polygon_url=...&raster_url=...')
  .then(response => response.blob())  // Get body as Blob (binary data)
  .then(blob => {
    // Create download link
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'zonal_stats.fgb';  // Filename
    document.body.appendChild(a);
    a.click();  // Trigger download
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
```

### Option 2: Save to variable and process
```javascript
fetch('/zonal_stats?polygon_url=...&raster_url=...')
  .then(response => response.arrayBuffer())  // Get body as ArrayBuffer
  .then(buffer => {
    // buffer contains the file bytes
    console.log('File size:', buffer.byteLength);
    
    // You can process it, or save it:
    const blob = new Blob([buffer]);
    const url = URL.createObjectURL(blob);
    // ... download code from Option 1
  });
```

### Option 3: Read as stream (for large files)
```javascript
const response = await fetch('/zonal_stats?polygon_url=...&raster_url=...');
const reader = response.body.getReader();
const chunks = [];

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  chunks.push(value);  // value is Uint8Array chunk
}

// Combine chunks
const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
const result = new Uint8Array(totalLength);
let offset = 0;
for (const chunk of chunks) {
  result.set(chunk, offset);
  offset += chunk.length;
}

// Now result contains all file bytes
```

## Using Python requests

```python
import requests

response = requests.get('http://localhost:8000/zonal_stats', params={
    'polygon_url': '...',
    'raster_url': '...'
})

# response.content contains the file bytes
print(f"Received {len(response.content)} bytes")

# Save to file
with open('zonal_stats.fgb', 'wb') as f:
    f.write(response.content)  # Write body bytes to disk
```

## The Key Point

The **response body** contains the file bytes. You need to:
1. Read the body (curl does this automatically, fetch/requests require calling `.blob()` or `.content`)
2. Write those bytes to a file on disk

The browser does this automatically when it sees `Content-Disposition: attachment`, but with curl/fetch you control it.


