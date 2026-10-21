import * as exifr from 'exifr';

function loadImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => resolve({ image, url });
    image.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error(`无法读取照片：${file.name}`));
    };
    image.src = url;
  });
}

async function readMetadata(file) {
  const [dateInfo, gpsInfo] = await Promise.all([
    exifr.parse(file, ['DateTimeOriginal', 'CreateDate', 'DateTimeDigitized']).catch(() => undefined),
    exifr.gps(file).catch(() => undefined),
  ]);
  const capturedAt = dateInfo?.DateTimeOriginal ?? dateInfo?.CreateDate ?? dateInfo?.DateTimeDigitized ?? null;
  return {
    capturedAt: capturedAt instanceof Date ? capturedAt : capturedAt ? new Date(capturedAt) : null,
    latitude: gpsInfo?.latitude,
    longitude: gpsInfo?.longitude,
  };
}

export async function preparePhotos(files, routeScene) {
  const accepted = [...files].filter((file) => file.type.startsWith('image/')).slice(0, 12);
  const photos = [];

  for (let index = 0; index < accepted.length; index += 1) {
    const file = accepted[index];
    const [{ image, url }, metadata] = await Promise.all([loadImage(file), readMetadata(file)]);

    let method = '平均分布';
    let progress = (index + 1) / (accepted.length + 1);
    if (Number.isFinite(metadata.latitude) && Number.isFinite(metadata.longitude)) {
      progress = routeScene.progressForCoordinate(metadata.latitude, metadata.longitude);
      method = '照片 GPS';
    } else if (metadata.capturedAt && !Number.isNaN(metadata.capturedAt.getTime())) {
      const timeProgress = routeScene.progressForTimestamp(metadata.capturedAt);
      if (timeProgress != null) {
        progress = timeProgress;
        method = '拍摄时间';
      }
    }

    photos.push({
      id: crypto.randomUUID(),
      file,
      image,
      url,
      capturedAt: metadata.capturedAt,
      progress,
      method,
      automaticProgress: progress,
      automaticMethod: method,
      isCover: false,
      label: file.name.replace(/\.[^.]+$/, ''),
    });
  }

  return photos;
}

export function releasePhotos(photos) {
  for (const photo of photos) URL.revokeObjectURL(photo.url);
}
