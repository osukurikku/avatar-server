import peewee
import peewee_async
from config import config

db = peewee_async.MySQLDatabase(
    config['db']['database'],
    user=config['db']['user'],
    password=config['db']['password'],
    host=config['db']['host'],
    port=3306
)

manager = peewee_async.Manager(db)
db.set_allow_sync(False)

async def get_or_none(model, *args, **kwargs):
    try:
        return await manager.get(model, *args, **kwargs)
    except peewee.DoesNotExist:
        return None


class BaseModel(peewee.Model):
    class Meta:
        database = manager.database


class users(BaseModel):
    username = peewee.CharField()
    privileges = peewee.IntegerField()
    donor_expire = peewee.BigIntegerField()


class tokens(BaseModel):
    user = peewee.IntegerField()
    privileges = peewee.IntegerField()
    private = peewee.IntegerField()
    token = peewee.CharField()
