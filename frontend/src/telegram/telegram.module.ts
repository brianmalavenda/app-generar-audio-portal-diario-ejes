const { Module } = require('@nestjs/common');
const { TelegramService } = require('./telegram.service');
const { TelegramController } = require('./telegram.controller');

@Module({
  providers: [TelegramService],
  controllers: [TelegramController],
  exports: [TelegramService],
})

export class TelegramModule {}