


# Pelin alustus:

Ennen kuin peli pyörii se vaatii alustamista:

importtaa src kansio:
>> from src import *


luo gamedata olio:
>> gamedata = Gamedata(moninpeli:bool,server:bool):

lue kartan tiedot:
>> mapstr, gamedata.map_height_, gamedata.map_width_,gamedata.required_score_,timelimit = ReadMapFile(map_file_path) #moninpelissä client saa nämä tiedot socketin kautta

aseta mapstr gamedata olioon:
>> SetMap(gamedata, mapstr) #muuttaa merkkijonon pelin kartaksi ja asettaa sen gamedata olioon

tämän jälkeen pitää asettaa näytön resoluutio  ja alustaa piirtoalue
>> gamedata.SetScreenSize((1280,720))  # set screen size
>> gamedata.SetDrawarea()

tämän jälkeen pelin alustus on valmis ja se voidaan aloittaa mikäli se on yksinpeli:
>> Run(gamedata:object,connection:object = None)



# Moninpeli:


## CLIENT:

luo client olion ja yrittää yhdistää serveriin:
>> connection = Client(ip-osoite,portti)  #create connection object


jos yhteys luotu onnistuneesti
voi tarkistaa näin:
>> if connection.connected_: #if the connection was successful

client lähettää viestin että on valmis aloittamaan pelin ja lähettää liittymis tunnuksen:
>> connection.SendReadyToStart(gameid)



serveri vastaa tähän lähettämällä aloitusinfon, odotetaan näitä

joten sockettia pitää lukea:

>> connection.read()

varmista että pakeetti on aloitusinfo ja lue se:
>> if connection.data_type_ == "startinfo":  #if start info
>
> gamedata.map_height_, gamedata.map_width_,gamedata.required_score_ = connection.data_ #set map size and required_score

heti tämän perään lue kartta
>> connection.Read()  # read messages
> 
>> if connection.data_type_ == "map":  #if message is map

aseta kartta:
>> SetMap(gamedata, connection.data_,True)  #set map


tämän jälkeen pitää pelin sujuvuuden takia asettaa uusi timeout socketille:
>> connection.SetTimeout(0.01) #set new timeout

Pelinalustus on valmis, käynnistä se:
>> Run(gamedata:object,connection:object = None)


## SERVER:
lataa kartta

luo Server olio:
ja odottaa aikakatkaisun verran yhdistääkö joku:

>> connection = Server(port,timeout) #create connection object

tarkista yhdistikö joku:
>> if connection.connected_: #if someone connected


jos yhdisti lue viesti:
 >> connection.Read()  # read messages

tarkista viestin tyyppi ja tarkista liittymistunnus:

>> if connection.data_type_ == "readytostart":  # if client ready to start the game 
> 
>> if connection.data_ == join_id:

lähetä clientille kartan koko, vaadittavat pisteet, kartan aikaraja:

>> connection.SendStartInfo(map_height,map_width,required_score,timelimit)  # send start info

tämän jälkeen pittää lähettää kartta clientille:
>> connection.SendMap(gamedata.current_map_, 0)  #send map


näytön asetukset pitää alustaa:
>> gamedata.SetScreenSize((resoluutio_x, resoluutio_y))  # set screen size
>> gamedata.SetDrawarea()


ja soccketille pitää asettaa uusi timeout:
>> connection.SetTimeout(0.01) #set new timeout

Pelin alustus on valmis, käynnistä se:
>> Run(gamedata:object,connection:object = None)


# Run() funktio

Run(gamedata:object,connection:object = None)

funktio on itse pelin pääfunktio ja paluattaa True/False riippuen päästinkö kartta läpi













