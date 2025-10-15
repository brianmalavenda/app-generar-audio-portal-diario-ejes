const { Injectable, Logger } = require('@nestjs/common');
import { createReadStream } from 'fs';
import { join } from 'path';

// ✅ Forma correcta de importar
const TelegramBot = require('node-telegram-bot-api');

@Injectable()
export class TelegramService {
  private readonly logger = new Logger(TelegramService.name);
  private bot: any; // O TelegramBot si funciona el tipado

  constructor() {
    this.bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, { 
      polling: false 
    });
  }

  /**
   * Envía el audio a un chat de Telegram
   */
  async sendFileToChat(
    chatId: string,
    fileName?: string
  ): Promise<any> {
    try {
      console.log("en el service de telegram, sendFileToChat");
      this.logger.log(`Enviando audio al chat: ${chatId}`);

      // Leer el archivo desde el sistema de archivos
      const filePath = join(process.cwd(), `shared/diario_procesado/${fileName}`);
      const file = createReadStream(filePath);

      const fs = require('fs');
      const stats = fs.statSync(filePath);
      const sizeInMB = stats.size / (1024 * 1024);

      this.logger.log(`Tamaño del archivo: ${sizeInMB.toFixed(2)}MB`);

      if (sizeInMB > 50) {
        throw new Error(`El archivo es muy grande (${sizeInMB.toFixed(2)}MB). Máximo: 50MB`);
      } 

      const result = await this.bot.sendFile(chatId, file, {
        caption: `🎵 ${fileName}`,
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