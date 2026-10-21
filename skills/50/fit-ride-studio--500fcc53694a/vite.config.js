import fs from 'node:fs';
import path from 'node:path';
import { defineConfig } from 'vite';
import { REPORT_RUNTIME_PREFIX, REPORT_RUNTIME_ROOT, REPORT_SESSION_TTL_MS } from './scripts/prepare-report.mjs';

const allowedExtensions = new Set(['.fit', '.kml', '.json']);
const contentTypes = {
  '.fit': 'application/octet-stream',
  '.kml': 'application/vnd.google-earth.kml+xml; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
};

function send(response, statusCode, message) {
  response.statusCode = statusCode;
  response.setHeader('Content-Type', 'text/plain; charset=utf-8');
  response.end(message);
}

export default defineConfig({
  plugins: [
    {
      name: 'ride-relief-runtime-files',
      configureServer(server) {
        server.middlewares.use(async (request, response, next) => {
          const requestUrl = new URL(request.url ?? '/', 'http://127.0.0.1');
          if (!requestUrl.pathname.startsWith(REPORT_RUNTIME_PREFIX)) return next();
          if (!['GET', 'HEAD'].includes(request.method ?? 'GET')) return send(response, 405, 'Method not allowed');

          try {
            const encodedPath = requestUrl.pathname.slice(REPORT_RUNTIME_PREFIX.length);
            const relativePath = decodeURIComponent(encodedPath);
            const target = path.resolve(REPORT_RUNTIME_ROOT, relativePath);
            const relative = path.relative(REPORT_RUNTIME_ROOT, target);
            if (!relative || relative.startsWith('..') || path.isAbsolute(relative)) {
              return send(response, 403, 'Invalid runtime path');
            }

            const extension = path.extname(target).toLowerCase();
            if (!allowedExtensions.has(extension)) return send(response, 403, 'Unsupported runtime file');

            const sessionDirectory = path.join(REPORT_RUNTIME_ROOT, relative.split(path.sep)[0]);
            const [runtimeRoot, realTarget, details, sessionDetails] = await Promise.all([
              fs.promises.realpath(REPORT_RUNTIME_ROOT),
              fs.promises.realpath(target),
              fs.promises.stat(target),
              fs.promises.stat(sessionDirectory),
            ]);
            if (Date.now() - sessionDetails.mtimeMs > REPORT_SESSION_TTL_MS) {
              return send(response, 410, 'Report session expired');
            }
            const realRelative = path.relative(runtimeRoot, realTarget);
            if (!details.isFile() || realRelative.startsWith('..') || path.isAbsolute(realRelative)) {
              return send(response, 403, 'Invalid runtime file');
            }

            response.statusCode = 200;
            response.setHeader('Cache-Control', 'no-store');
            response.setHeader('Content-Type', contentTypes[extension]);
            response.setHeader('X-Content-Type-Options', 'nosniff');
            response.setHeader('Content-Length', details.size);
            if (request.method === 'HEAD') return response.end();
            fs.createReadStream(realTarget).pipe(response);
          } catch (error) {
            if (error?.code === 'ENOENT') return send(response, 404, 'Runtime file not found');
            server.config.logger.error(`Runtime file error: ${error.message}`);
            return send(response, 500, 'Runtime file error');
          }
        });
      },
    },
  ],
});
