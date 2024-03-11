import time
mana = 60
health = 200
starvation = 70
current_state = 'resting'
loopCount = 0

while current_state != 'dead':
    if loopCount == 50:
        break
    if current_state == "resting":
        print("currently resting and restoring mana")
        mana += 10
        print ("Mana: ", mana, "Starvation: ", starvation, "Health: ", health)
        print("========================================================================")
        if mana > 40:
            current_state = "idle"
    
    elif current_state == "idle":
        print("currnetly idling, mana and starvation will slowly decrease")
        mana -= 10
        starvation -= 5
        print ("Mana: ", mana, "Starvation: ", starvation, "Health: ", health)
        print("========================================================================")        
        if starvation < 30:
            current_state = "hungry"
        if mana < 15:
            current_state = "resting"
    
    elif current_state == "hungry":
        print("currently hungry, health will be decrease")
        health -= 15
        print ("Mana: ", mana, "Starvation: ", starvation, "Health: ", health)
        print("========================================================================")        
        if health < 50:
            current_state = "healing"
    
    elif current_state == "healing":
        print("currently healing, your health and starvation will be increase, but mana will be decrease")
        health += 20
        starvation += 5
        mana -= 10
        print ("Mana: ", mana, "Starvation: ", starvation, "Health: ", health)
        print("========================================================================")        
        if health > 150 or health < 210 and mana > 40:
            current_state = "idle"
        elif mana < 15 and health < 210:
            current_state = "resting"
        
    time.sleep(1)         
    loopCount += 1   


