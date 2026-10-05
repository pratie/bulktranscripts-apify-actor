# YouTube Transcripts in Bulk: Channels, Playlists & Videos

Get clean transcripts for **every video in a YouTube channel or playlist** (up to 1,000 per source), or for any list of single videos. One dataset row per video with the full text, paragraphs, title, channel, duration and upload date, plus timestamped segments if you want them.

Powered by [BulkTranscripts](https://bulktranscripts.co), the YouTube transcript service behind the BulkTranscripts web app, API and MCP server.

## What you can do with it

- **Research a creator or a whole niche.** Pull 500 videos from a channel and feed them to ChatGPT, Claude or NotebookLM.
- **Build a dataset.** Export JSON, CSV or Excel straight from the Apify dataset for analysis, search or RAG.
- **Monitor channels on a schedule.** Run it daily with Apify Schedules; videos you already have are not charged again.
- **Feed automations.** Connect the dataset to Make, Zapier, n8n, Google Sheets or a webhook with Apify integrations.

## Try it without a key

Click **Start** with the example input and leave the API key empty: the example video runs free, so you can see the output before signing up. Your own videos, playlists and channels need a key.

## How to use it

1. **Get a BulkTranscripts API key.** Sign in at [bulktranscripts.co/app](https://bulktranscripts.co/app?tab=mcp) and create a key in the MCP & API tab. New accounts include **30 free transcripts**, no card needed.
2. **Paste your YouTube links** into *YouTube URLs*, one per line: videos, playlists or channels (`https://www.youtube.com/@TED` works).
3. **Paste your API key** into *BulkTranscripts API key* and click **Start**.

Single videos come back in a second or two. Channels and playlists run as one job on BulkTranscripts' servers; a few hundred new videos usually take a few minutes.

## Input

| Field | What it does |
|---|---|
| `urls` | Videos, playlists and channels, one per line. |
| `apiKey` | Your BulkTranscripts API key (or the license key from a credit pack). Stored as a secret. Optional for the example video only. |
| `maxVideos` | Most videos to take from each channel or playlist (1 to 1,000, default 50). Channels start with the newest uploads. |
| `language` | Preferred caption language code, e.g. `en`, `es`, `de`. Falls back to the video's available captions. |
| `includeSegments` | Add timestamped segments (start, duration, text) to each row. |

## Output

One row per video:

```json
{
  "videoId": "fNk_zzaMoSs",
  "url": "https://www.youtube.com/watch?v=fNk_zzaMoSs",
  "title": "Vectors | Chapter 1, Essence of linear algebra",
  "channel": "3Blue1Brown",
  "status": "ok",
  "language": "en",
  "captionSource": "manual_caption",
  "wordCount": 1800,
  "durationSeconds": 592,
  "uploadDate": "2016-08-05",
  "transcript": "The fundamental, root-of-it-all building block for linear algebra is the vector...",
  "paragraphs": ["The fundamental, root-of-it-all building block...", "..."],
  "sourceUrl": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab"
}
```

Videos without a transcript get a row too, with `status` saying why (for example `no_transcript`, `members_only`, `private_video`) and no charge.

## Pricing

The Actor itself is free to run on Apify; a run uses very little compute because the extraction happens on BulkTranscripts' servers.

Transcripts use **BulkTranscripts credits**: one credit per new transcript. Videos already in your BulkTranscripts library are free to fetch again, forever, in any format. Every account starts with 30 free credits; packs start at $4.99 for 200 transcripts and never expire. See [bulktranscripts.co/#pricing](https://bulktranscripts.co/#pricing).

If your balance runs out mid-run, the Actor saves everything fetched so far and stops with a message; add credits and run again, and the videos you already have cost nothing.

## FAQ

**Which videos work?** Any public or unlisted video with captions, manual or auto-generated. Members-only, private and age-restricted videos are reported, not charged.

**My playlist returns nothing.** Private playlists can only be read by their owner. Set the playlist to *Unlisted* in YouTube Studio and run again.

**How fast is it?** Bulk extraction runs on BulkTranscripts' servers in parallel. Reading finished transcripts back into the dataset is rate-limited to about 30 per minute, so a 1,000-video channel takes roughly half an hour end to end.

**Can I use the same credits elsewhere?** Yes. The same account works in the [BulkTranscripts web app](https://bulktranscripts.co/app), the [REST API](https://bulktranscripts.co/docs) and the [MCP server](https://bulktranscripts.co/youtube-mcp-server) for ChatGPT, Claude and Cursor.

## Support

Questions or a video that should work but doesn't: hello@bulktranscripts.co.

BulkTranscripts is not affiliated with YouTube or Google.
