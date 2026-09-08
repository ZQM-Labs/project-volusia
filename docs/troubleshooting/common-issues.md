# Troubleshooting Guide — Project Volusia

> Common issues and their solutions.

---

## Backend Issues

### Portal won't start

**Symptom**: `python portal_app.py` fails to start

**Solutions**:
1. Check Python version: `python --version` (need 3.11+)
2. Install dependencies: `pip install -r requirements.txt`
3. Check port availability: `netstat -ano | findstr :8789`
4. Check database path: `ls Tools/volusia_data/volusia.db`

### Data not refreshing

**Symptom**: Indicators show stale data

**Solutions**:
1. Run refresh manually: `cd Tools/volusia_data && python refresh_v2.py`
2. Check audit log: `sqlite3 volusia.db "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 10;"`
3. Verify API keys are set (if required)
4. Check network connectivity to data sources

### Database locked

**Symptom**: `database is locked` error

**Solutions**:
1. Close other connections to the database
2. Restart the portal service
3. Check for zombie processes: `ps aux | grep portal_app`

---

## Frontend Issues

### Blank page on load

**Symptom**: White screen when visiting https://volusia.zqmlabs.com

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify `dist/` folder exists in `gh-pages` branch
3. Check GitHub Actions build status
4. Clear browser cache and reload

### Charts not rendering

**Symptom**: Nivo charts show as blank areas

**Solutions**:
1. Check if `@nivo/*` packages are installed: `npm ls @nivo/core`
2. Verify data format matches expected schema
3. Check browser console for D3 errors
4. Try a different browser

### Map not loading

**Symptom**: Leaflet map shows gray background

**Solutions**:
1. Check internet connection (tiles load from OpenStreetMap)
2. Verify Leaflet CSS is loaded: `link[rel="stylesheet"]` in page source
3. Check for JavaScript errors in console
4. Try zooming in/out to trigger tile reload

---

## Deployment Issues

### GitHub Actions build fails

**Symptom**: Red X on commit, no deployment

**Solutions**:
1. Check Actions tab: https://github.com/ZQM-Computing/volusia-portal/actions
2. Review build logs for errors
3. Verify `package.json` scripts are correct
4. Check for TypeScript errors: `npx tsc --noEmit`

### Custom domain not working

**Symptom**: `volusia.zqmlabs.com` doesn't resolve

**Solutions**:
1. Check DNS: `nslookup volusia.zqmlabs.com`
2. Verify CNAME file exists in `gh-pages` branch
3. Check Cloudflare DNS settings
4. Wait for DNS propagation (up to 24 hours)

### Cloudflare Tunnel down

**Symptom**: `volusia.zqmlabs.com/api` returns 502

**Solutions**:
1. Check tunnel status: `cloudflared tunnel list`
2. Restart tunnel: `cloudflared tunnel run volusia`
3. Verify backend is running: `curl http://localhost:8790/api/health`
4. Check Cloudflare dashboard for tunnel errors

---

## Data Issues

### Missing indicators

**Symptom**: Some indicators show "—" or no data

**Solutions**:
1. Check if indicator exists in database: `sqlite3 volusia.db "SELECT * FROM indicators WHERE name='indicator_name';"`
2. Run data refresh: `python refresh_v2.py`
3. Check source API status (may be down)
4. Verify data format matches expected schema

### Incorrect values

**Symptom**: Values seem wrong or outdated

**Solutions**:
1. Check `fetched_at` timestamp: `sqlite3 volusia.db "SELECT name, fetched_at FROM indicators;"`
2. Compare with source website
3. Check for data transformation errors in pipeline
4. Verify unit conversions are correct

---

## Performance Issues

### Slow page load

**Symptom**: Pages take more than 3 seconds to load

**Solutions**:
1. Check network tab in browser dev tools
2. Verify JSON files are compressed (gzip)
3. Check if CDN is serving static assets
4. Consider implementing caching headers

### API rate limiting

**Symptom**: `429 Too Many Requests` errors

**Solutions**:
1. Implement client-side caching
2. Reduce polling frequency
3. Use conditional requests (ETag/If-Modified-Since)
4. Contact ZPM Labs to increase rate limits

---

## Getting Help

If your issue isn't listed here:

1. Check existing issues: https://github.com/ZQM-Labs/project-volusia/issues
2. Create a new issue with:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment info
3. Join the community (if available)

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
