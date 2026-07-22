Enhanced version of Home Assistant's built-in qBittorrent integration

Adds the following features:
- Additional sensors showing:
    * How many torrents are still in 'downloading' state
    * The longest ETA of all downloading torrents 

- Events can be raised whenever a torrent is added, completed or removed (at the users' choice)
```yaml
qbittorrent_torrent_complete
qbittorrent_torrent_added
qbittorrent_torrent_removed
```
- Four new services:
    * Pause/resume all torrents, or a specific torrent via an optional hash
    * Delete a specific torrent, optionally including the associated files as well
    * Return information on all torrents, or a specific torrent via an optional hash
    * Shut down the remote qBittorrent client
## Startup / offline qBittorrent behavior

This build uses a short HTTP timeout (1 second to connect, 2 seconds to read) and no longer performs network authentication while Home Assistant is setting up the integration. If the qBittorrent PC is powered off, Home Assistant can complete startup normally. The sensors remain unavailable and retry authentication during their normal update cycle; when qBittorrent becomes available, the integration reconnects automatically.

