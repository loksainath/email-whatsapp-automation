const puppeteerPath = require("./puppeteer_path");

const client = new Client({
  authStrategy: new LocalAuth({
    clientId: "email_whatsapp_bot_v1",
    dataPath: "./.wwebjs_auth"
  }),
  puppeteer: {
    headless: false,
    executablePath: puppeteerPath.executablePath,
    defaultViewport: null,
    args: ["--start-maximized"]
  }
});
