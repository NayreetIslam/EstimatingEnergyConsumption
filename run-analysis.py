
#### Group 5 -- Sifat and Nayreet

INPUT_FILE = "COOJA.testlog"

# From Z1 node datasheet
CURRENT_MA = {
    "CPU" : 10,
    "LPM" : 0.023,
    "Deep LPM" : 0, # not used by Z1 nodes
    "Radio Rx" : 18.8,
    "Radio Tx" : 17.4,
}

STATES = list(CURRENT_MA.keys())

VOLTAGE = 3.0 # assume 3 volt batteries
RTIMER_ARCH_SECOND = 32768

def main():
    node_ticks = {}
    node_total_ticks = {}
    
    with open(INPUT_FILE, "r") as f:
        for line in f:
            if "INFO: Energest" not in line:
                continue
            fields = line.split()
            #print(fields)
            try:
                #######################Sample Line###############################
                #05:00.236	ID:2	[INFO: Energest  ] Total time  :   60000000
                ###############Parsed ID based on ':' Character###################
                #print("ID: "+fields[1].split(":")[1])
                node = int(fields[1].split(":")[1])
            except:
                continue

            if node not in node_ticks:
                # initialize to zero
                node_ticks[node] = { u : 0  for u in STATES }
                node_total_ticks[node] = 0

            try:
                state_index = 5
                state = fields[state_index]
                tick_index = state_index + 2
                if state not in STATES:
                    #print("State Index: "+fields[state_index])
                    #print("State Index + 1: "+fields[state_index+1])
                    state = fields[state_index] + " " + fields[state_index+1]
                    #print("State: "+state)
                    tick_index += 1
                    if state not in STATES:
                        # add to the total time
                        if state == "Total time":
                            node_total_ticks[node] += int(fields[tick_index])
                        continue
                # add to the time spent in specific state
                ticks = int(fields[tick_index][:-1]) ###### Parsing Ticks based on ':' character
                #print("Ticks "+str(ticks))
                node_ticks[node][state] += ticks
            except Exception as ex:
                print("Failed to process line '{}': {}".format(line, ex))

    nodes = sorted(node_ticks.keys())
    for node in nodes:
        total_avg_current_mA = 0
        period_ticks = node_total_ticks[node]
        period_seconds = period_ticks / RTIMER_ARCH_SECOND
        for state in STATES:
            ticks = node_ticks[node].get(state, 0)
            current_mA = CURRENT_MA[state]
            ############### Validating formula params #################
            #print("Ticks "+ str(ticks))
            #print("current_mA  "+str(current_mA))
            #print("period_ticks  "+str(period_ticks))
            #print("VOLTAGE  "+str(VOLTAGE))
            ###########################################################
            if period_ticks == 0:
                state_avg_current_mA = ticks * current_mA / 1
            else:
                state_avg_current_mA = ticks * current_mA / period_ticks
            total_avg_current_mA += state_avg_current_mA
        total_charge_mC = period_ticks * total_avg_current_mA / RTIMER_ARCH_SECOND
        total_energy_mJ = total_charge_mC * VOLTAGE
        print("Node {}: {:.2f} mC ({:.3f} mAh) charge consumption, {:.2f} mJ energy consumption in {:.2f} seconds".format(
            node, total_charge_mC, total_charge_mC / 3600.0, total_energy_mJ, period_seconds))

if __name__ == "__main__":
    main()
