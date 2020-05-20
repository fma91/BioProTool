import kivy
kivy.require('1.11.1')
 
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint
import pandas as pd


from kivy.config import Config
Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '600')



class CalcBoxLayout(BoxLayout):
	#Monod sólo sustrato
	class Monod_basic():  
		def __init__(self,substrate,S,X,P):    
			
			self.substrate = substrate.lower().replace(' ', '').replace('\t','')
			self.carbon = {'glc': [0.87, 0.1, 2.5,100],'glyc': [0.5, 0.12, 3, 80],'ac': [0.4, 0.15, 3.2, 20]} 
			self.MUmax = self.carbon[self.substrate][0]
			self.Ks = self.carbon[self.substrate][1]
			self.Ysx = self.carbon[self.substrate][2]
			self.Is = self.carbon[self.substrate][3]
			if P == '':
				self.c = [X,S,P]
				print(self.c[:2])
			else:
				self.c = [X,S,float(P)]
    
		def ODE(self,c,t):  #definición de ecuación diferencial
			x = c[0]
			s = c[1] 
			if len(c)>2:
				p = c[2]
				dxdt =  (1 - (p/15) ) * (1 - (s/self.Is) ) * self.MUmax * s / (self.Ks * (1 - (s/self.Is) * (1 - (p/15) )) + s ) * x
				dsdt = -((1 - (p/15) ) * (1 - (s/self.Is) ) * self.MUmax * s / (self.Ks * (1 - (s/self.Is) * (1 - (p/15) ) ) + s ) * x * self.Ysx) - ((1 - (float(p)/15) ) * (1 - (s/self.Is) ) * self.MUmax * s / (self.Ks * (1 - (s/self.Is) ) * (1 - (float(p)/15) ) + s ) * x *0.75)
				dpdt = (1 - (float(p)/15) ) * (1 - (s/self.Is) ) * self.MUmax * s / (self.Ks * (1 - (s/self.Is) ) * (1 - (float(p)/15) ) + s ) * x *0.75
				return np.array([dxdt,dsdt,dpdt])
				
			else:
				dxdt = (1 - (s/self.Is) ) * self.MUmax * s / (self.Ks * (1 - (s/self.Is)) + s ) * x
				dsdt = - (1 - (s/self.Is) ) * self.MUmax * s / (self.Ks * (1 - (s/self.Is)) + s ) * x * self.Ysx
				return np.array([dxdt,dsdt])


		def solve(self,t):
			self.t = np.linspace(0 ,t,100)
			if self.c[2] == '':
				self.sol = odeint(self.ODE,self.c[:2],self.t)
			else:
				self.sol = odeint(self.ODE,self.c,self.t) 
			self.mu =  self.MUmax*self.sol[:,1]/(self.Ks+self.sol[:,1])
			self.qs =  self.MUmax*self.sol[:,1]/(self.Ks+self.sol[:,1])*self.Ysx
                
		def plot(self):
			plt.plot(self.t,self.sol)
			plt.xlim(0,max(self.t))
			plt.ylim(0,max(self.sol[:,1]))
			plt.xlabel('Time h')
			if self.c[2]=='':
				plt.legend(['Biomass',self.substrate.upper()],loc=0)
				plt.ylabel('Biomass / {} g/L'.format(self.substrate) )
			else:
				plt.legend(['Biomass',self.substrate.upper(),'Product'],loc=0)
				plt.ylabel('Biomass / {} g/L'.format(self.substrate) )
			plt.show()

		def data_frame(self,col_name,data_table):
			if self.c[2] == '':
				table_array=np.array(data_table)
				table = pd.DataFrame(columns=col_name[0:-1],data=table_array[:,:3])
			else:
				table = pd.DataFrame(columns=col_name,data=data_table)
			return table


class BioproApp(App):
	def build(self):
		return CalcBoxLayout()

BioproApp().run()
