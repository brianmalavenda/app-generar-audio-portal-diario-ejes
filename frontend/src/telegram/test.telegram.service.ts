const { Injectable, Logger, StreamableFile } = require ('@nestjs/common');
const { createReadStream } = require('fs');
const { join } = require('path');
const TelegramBot = require('node-telegram-bot-api');

@Injectable()
export class TelegramService {
  private readonly logger = new Logger(TelegramService.name);
  private bot: typeof TelegramBot;
  private storage: Storage;

  constructor() {
    this.bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, { 
      polling: false 
    });
    this.storage = new Storage();
  }

  /**
   * Envía el audio a un chat de Telegram
   */
  async sendAudioToChat(
    chatId: string, // obtener el chatId
    fileName?: string
  ): Promise<any> {
    try {
      //file es un documento tipo word
      const file = createReadStream(join(process.cwd(),`shared/diario_procesado/${fileName}`));
      // Verificar tamaño (Telegram limita a 50MB)
      const sizeInMB = file.readableLength / (1024 * 1024);
      if (sizeInMB > 50) {
        throw new Error(`El archivo es muy grande (${sizeInMB.toFixed(2)}MB). Máximo: 50MB`);
      }

      const audioStream = new StreamableFile(file, {
        type: 'application/json',
        disposition: `attachment; filename="${fileName}"`,
      });
      // Convertir buffer a stream
      // const audioStream = Readable.from(audioBuffer);

      // Enviar a Telegram
      const result = await this.bot.sendAudio(chatId, audioStream, {
        caption: `${fileName}`,
        title: fileName,
        performer: 'Text-to-Speech',
      });

      this.logger.log(`Audio enviado exitosamente. Message ID: ${result.message_id}`);
      return result;

    } catch (error) {
      this.logger.error('Error enviando audio a Telegram:', error);
      throw error;
    }
  }

  /**
   * Obtiene información del bot
   */
  async getBotInfo() {
    try {
      const info = await this.bot.getMe();
      return info;
    } catch (error) {
      this.logger.error('Error obteniendo info del bot:', error);
      throw error;
    }
  }
}