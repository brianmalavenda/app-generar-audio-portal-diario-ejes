const { Controller, Post, Body, Get, HttpException, HttpStatus } = require('@nestjs/common');
import { TelegramService } from './telegram.service';

// DTO con interfaz TypeScript
interface ShareTelegramDto {
  chatId: string;
  fileName?: string;
}

@Controller('telegram')
export class TelegramController {
  constructor(private readonly telegramService: TelegramService) {}

  @Post('share-files')
  async shareFiles(@Body() shareTelegramDto: ShareTelegramDto) {
    try {
      console.log("En el controller de telegram, shareFiles");
      const result = await this.telegramService.sendFileToChat(
        shareTelegramDto.chatId,
        shareTelegramDto.fileName,
      );

      console.log('Resultado del envío de archivo:', result);

      return {
        success: true,
        message: 'Audio compartido exitosamente',
        messageId: result.message_id,
      };
    } catch (error) {
      throw new HttpException(
        {
          success: false,
          message: error.message || 'Error compartiendo audio',
        },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('bot-info')
  async getBotInfo() {
    try {
      const info = await this.telegramService.getBotInfo();
      return {
        success: true,
        bot: info,
      };
    } catch (error) {
      throw new HttpException(
        {
          success: false,
          message: 'Error obteniendo información del bot',
        },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}