# -*- coding: utf-8 -*-
"""Untitled15.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KGEAnev7TVY2Yq4GzFXkjaAnfAeQUkgi
"""

import numpy as np
from scipy.integrate import solve_ivp
import tensorflow as tf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.losses import MeanAbsoluteError
from tensorflow.keras.losses import MeanAbsolutePercentageError
from tensorflow.keras.losses import Huber

from keras.models import load_model

# load the saved model
model1 = load_model('initmy_model.h5')

"""# Create the data matrix and plot the Lorenz system """

def make_points_smaller(initial_conditions, rho, sigma=10, beta=8/3, timestep=10000 ):

  WIDTH, HEIGHT, DPI = 1000, 750, 100

  # Initial conditions.

  u0, v0, w0 = initial_conditions

  # Maximum time point and total number of time points.
  tmax, n = 100, timestep

  def lorenz(t, X, sigma, beta, rho):
    """The Lorenz equations."""
    x,y,z = X
    ux = sigma*(y - x)
    uy = x*(rho-z)-y
    uz = x*y-beta*z
    return ux, uy, uz

  # Integrate the Lorenz equations.
  soln = solve_ivp(lorenz, (0, tmax), (u0, v0, w0), args=(sigma, beta, rho),
                    dense_output=True)
    
  # Interpolate solution onto the time grid, t.
  t = np.linspace(0, tmax, n)
  x, y, z = soln.sol(t)

  M = np.array([x,y,z, np.repeat(rho,n)])
  # Plot the Lorenz attractor using a Matplotlib 3D projection.
  
  WIDTH, HEIGHT, DPI = 1000, 750, 100
  fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI))
  r = rho
  ax = fig.add_subplot(111, projection='3d')
  ax.plot(x, y, z)
  ax.set_xlabel('x')
  ax.set_ylabel('y')
  ax.set_zlabel('z')
  ax.set_title('Lorenz system (ρ=%d)'%r)
  plt.show()

  return M

"""Data for rho=10,28,40"""

m10= make_points_smaller([0,1,1],10)
m28= make_points_smaller([0,1,1],28)
m40= make_points_smaller([0,1,1],40)

# Combine all the training and testing data  

Train_all = np.hstack([m10,m28,m40])
Xall = Train_all[:,:-1]
Yall = Train_all[:,1:]


"""# Loop to find the best loss function """

loss_functions = [MeanSquaredError(), MeanAbsoluteError(), MeanAbsolutePercentageError(), Huber()]

# Loop through each loss function
for loss_func in loss_functions:
    print('Testing', loss_func.name)
    number_of_epochs = 150
    # Create an empty list to store the loss values for each epoch
    loss_values = []
    # Loop through each epoch value

        # Define the neural network model
    model = tf.keras.models.Sequential([
      tf.keras.layers.Dense(32, activation = 'relu',input_shape= (Train_all.shape[0],)),
      tf.keras.layers.Dense(32,activation = 'relu'),
      tf.keras.layers.Dense(3)

   ])
          #Compile the model 
        
    opt = tf.keras.optimizers.Adam(learning_rate=0.0005)


        # Compile the model with the current loss function
    model.compile(optimizer='adam', loss=loss_func)

        # Train the model with the current epoch value
    history = model.fit(Xall.T, Yall[:3,:].T,epochs=number_of_epochs,batch_size=10)

        # Add the final loss value to the list of loss values
    LOSS_LIST = list(history.history['loss'])
    loss_values.append(LOSS_LIST)

    # Plot the loss values for the current loss function
    plt.plot([i for i in range(number_of_epochs)], LOSS_LIST, label=loss_func.name)

# Add legend and labels to the plot
plt.legend()
plt.xlabel('t')
plt.ylabel('Loss')
plt.yscale('log')
plt.title('Regression Loss Functions Comparison')
plt.show()






"""# Model chosen after deciding with Huber Loss function"""

model1 = tf.keras.models.Sequential([
      tf.keras.layers.Dense(32, activation = 'relu',input_shape= (Xall.shape[0],)),
      tf.keras.layers.Dense(32,activation = 'relu'),
      tf.keras.layers.Dense(3)

])
          #Compile the model 
opt = tf.keras.optimizers.Adam(learning_rate=0.0005)


        # Compile the model with the current loss function
model1.compile(optimizer='adam', loss=Huber())

        # Train the model with the current epoch value
history1 = model1.fit(Xall.T, Yall[:3,:].T,epochs=150,batch_size=10)

# train and save the model
model1.save('initmy_model.h5')

"""# Function to get prediction matrix """

def get_pred_matrix(X, Y):

  rho = X[3,0]
  num =5000
  pred_matrix = np.zeros((num,4))

  pred1 = model1.predict(X[:,0:1].T,verbose=0) # has shape(1,3)
  pred_matrix[0,:] = np.append(pred1, rho) 

  for i in range(1,num):
    pred1 = model1.predict(pred_matrix[i-1,:].reshape((1,4)),verbose=0) # has shape (1,3)
    pred_matrix[i,:] = np.append(pred1, rho)

  return pred_matrix

"""# Creat X, Y matrices"""

def xy(matrix):
  x = matrix[:,:-1]
  y = matrix[:,1:]

  return x,y

"""X, Y matrices for each rho"""

x10,y10 = xy(m10)
x28,y28 = xy(m28)
x40,y40 = xy(m40)

"""Prediction matrix for each rho"""

pred_10 = get_pred_matrix(x10,y10)
pred_28 = get_pred_matrix(x28,y28)
pred_40 = get_pred_matrix(x40,y40)

"""# Function that plots the 3D plot """

def threed_plot(m,point):
  if m.shape[0]==4:
    d= m.T
  else :
    d=m

  
  pt=point 
  WIDTH, HEIGHT, DPI = 1000, 750, 100
  fig = plt.figure(figsize=(WIDTH/DPI, HEIGHT/DPI))
  ax = fig.add_subplot(111, projection='3d')
  ax.plot(d[:pt,0:1], d[:pt,1:2], d[:pt,2:3])
  ax.set_xlabel('x')
  ax.set_ylabel('y')
  ax.set_zlabel('z')
  plt.show()

"""# Function that plots the scatter plot """

def list_plot(y,p,pt):

  fig = plt.figure(figsize=(7,7))
  plt.plot([i for i in range(pt)], p[:pt,0],'ro', markersize=2,label="predicted")
  plt.plot([i for i in range(pt)], y.T[:pt,0],'bo', markersize=2,label="true")
  plt.xlabel("t")
  plt.ylabel("x(t)")
  plt.legend()
  plt.show()

# Plot 3D of rho=10,28,40 of the predicted data 
threed_plot(pred_10,1000)
threed_plot(m10,1000)

threed_plot(pred_28,1000)
threed_plot(m28,1000)

threed_plot(pred_40,1000)
threed_plot(m40,1000)


# List plot x(t) of predicted na dtrue 
list_plot(y10,pred_10,100)
list_plot(y28,pred_28,100)
list_plot(y40,pred_40,100)
list_plot(y40,pred_40,10)


# Function to compute error l2-norm 
def get_error_2(pred,y):

  error=[]
  s = pred.shape[0]
  r =pred[0,3]
  for i in range(s):
   l2 = np.linalg.norm(y[:,i:i+1].T-pred[i:i+1,:])

   
   
   error.append(l2)

  return error

# Function to create MSE 
def get_error(pred,y):

  error=[]
  s = pred.shape[0]
  r =pred[0,3]
  for i in range(s):
   mse = np.square(np.subtract(y[:,i:i+1].T, pred[i:i+1,:])).mean()

   
   
   error.append(mse)

  return error

# To change delta, simply replace timestep with the number of data points you want to generate

# Create rho=17,35 

matrix17 = make_points_smaller([0, 1, 1],17)
matrix35 = make_points_smaller([0, 1, 1],35)

x17,y17=xy(matrix17)
x35,y35=xy(matrix35)


pred_17 = get_pred_matrix(x17,y17)
pred_35 = get_pred_matrix(x35,y35)

# List plot rho=17,35

list_plot(y17,pred_17,1000)
list_plot(y17,pred_17,100)
list_plot(y17,pred_17,10)
list_plot(y35,pred_35,100)
list_plot(y35,pred_35,10)


# Compute the errors 

e1 = get_error(pred_10,y10)
e28 = get_error(pred_28,y28)
e40 = get_error(pred_40,y40)
e17 = get_error(pred_17,y17)
e35 = get_error(pred_35,y35)

e1 = get_error_2(pred_10,y10)
e28 = get_error_2(pred_28,y28)

# Plot the MSE 

fig = plt.figure(figsize=(7,7))
plt.plot([i for i in range(50)],e1[:50],label="ρ=10")
plt.plot([i for i in range(50)],e28[:50],label="ρ=28")
plt.plot([i for i in range(50)],e40[:50],label="ρ=40")
#plt.plot([i for i in range(50)],e17[:50],label="ρ=17")
#plt.plot([i for i in range(50)],e35[:50],label="ρ=35")
plt.legend()
plt.ylabel("MSE")
plt.xlabel("t")
plt.yscale("log")