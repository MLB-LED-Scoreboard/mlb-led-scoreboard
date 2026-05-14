import asyncio
from tesla_powerwall import Powerwall                                                                                                    
                                                                                                                                           
HOST     = "192.168.4.26"        # your Gateway IP or teg.local
PASSWORD = "mydgo6-muqbec-biRzis"                                                                                                               
EMAIL    = "twfarley@me.com"      # leave "" for older firmware                                                                          
   
async def main():                                                                                                                        
    pw = Powerwall(HOST, verify_ssl=False)                
    try:                                                                                                                                 
      await pw.login(PASSWORD, EMAIL)                   
      print("authenticated:", pw.is_authenticated())
      print(f"charge:   {await pw.get_charge():.1f}%")                                                                                 
      m = await pw.get_meters()
      print(f"solar:    {m.solar.get_power():+.2f} kW")                                                                                
      print(f"load:     {m.load.get_power():+.2f} kW")                                                                                 
      print(f"site:     {m.site.get_power():+.2f} kW")
      print(f"battery:  {m.battery.get_power():+.2f} kW")                                                                              
      print(f"mode:     {await pw.get_operation_mode()}")
      print(f"grid:     {await pw.get_grid_status()}")                                                                                 
    finally:                                              
        await pw.close()                                                                                                                 
                                                          
asyncio.run(main())
PY