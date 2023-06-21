from web3 import Web3
from datetime import datetime, date, timezone
from dateutil.relativedelta import relativedelta, TH
import time
import streamlit as st
from st_btn_select import st_btn_select
import yaml
import requests
import pandas as pd

# App
st.set_page_config(
    page_title="veCHR Checker",
    page_icon="icons/chr.png",
    layout="wide",
)

# Params
params_path = "params.yaml"


def read_params(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


config = read_params(params_path)

# Title
st.title("🔍 veCHR Checker")

# Check URL Params
query_params = st.experimental_get_query_params()

if not bool(query_params) == False:
    if 'id' in query_params:
        tokenid = int(query_params['id'][0])
        index = 0
    elif 'address' in query_params:
        wallet_address = query_params['address'][0]
        index = 1
    else:
        index = 0
else:
    index = 0


# Select Button
selection = st_btn_select(("Token ID", "Address"), index=index)

# CHR Price
params = {
    "from": "0x15b2fb8f08E4Ac1Ce019EADAe02eE92AeDF06851",
    "to": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
    "amount": "1000000000000000000",
}

try:
    response = requests.get("https://router.firebird.finance/arbitrum/route", params=params)
    CHR_price = response.json()["maxReturn"]["tokens"]["0x15b2fb8f08e4ac1ce019eadae02ee92aedf06851"]["price"]
except Exception as e:
    print(e)


try:
    provider_url = config["data"]["provider_url"]
    w3 = Web3(Web3.HTTPProvider(provider_url))

    abi1 = config["data"]["abi1"]
    contract_address1 = config["data"]["contract_address1"]
    contract_instance1 = w3.eth.contract(address=contract_address1, abi=abi1)

    abi2 = config["data"]["abi2"]
    contract_address2 = config["data"]["contract_address2"]
    contract_instance2 = w3.eth.contract(address=contract_address2, abi=abi2)

    abi3 = config["data"]["abi3"]
    contract_address3 = config["data"]["contract_address3"]
    contract_instance3 = w3.eth.contract(address=contract_address3, abi=abi3)

    # Total Supply
    totalSupply = contract_instance3.functions.balanceOf(contract_address1).call() / 1000000000000000000

    todayDate = datetime.utcnow()
    lastThursday = todayDate + relativedelta(weekday=TH(-1))
    my_time = datetime.min.time()
    my_datetime = datetime.combine(lastThursday, my_time)
    currentepoch = int(my_datetime.replace(tzinfo=timezone.utc).timestamp())

except Exception as e:
    print(e)

# Token ID Search
if selection == "Token ID":
    
    # URL Param Check
    try:
        if tokenid:
            pass
    except:
        tokenid = st.number_input("Your veCHR Token ID", min_value=1, format="%d")

    # Read Data
    try:
        # Balance veCHR
        bal = round(
            contract_instance1.functions.balanceOfNFT(tokenid).call() / 1000000000000000000,
            4,
        )

        # Locked veCHR
        locked = round(
            contract_instance1.functions.locked(tokenid).call()[0] / 1000000000000000000,
            4,
        )

        # Lock End Date
        lockend = time.strftime(
            "%Y-%m-%d",
            time.gmtime(int(contract_instance1.functions.locked(tokenid).call()[1])),
        )

        # Voted Last Epoch
        voted = contract_instance1.functions.voted(tokenid).call()

        # Voted Current Epoch
#         votedcurrentepoch = contract_instance2.functions.lastVoted(tokenid).call() > currentepoch

        # creating a single-element container
        placeholder = st.empty()

        # Empty Placeholder Filled
        with placeholder.container():
            if tokenid:
                st.markdown("🔒 Locked CHR: " + str(locked))
                st.markdown("🧾 veCHR Balance: " + str(bal))
                st.markdown("🤑 Estimated USD Value: $" + str(round(CHR_price * locked, 4)))
                st.markdown("⏲️ Lock End Date: " + str(lockend))
                st.markdown("🗳️ Vote Share: " + str(round(bal / totalSupply * 100, 4)) + "%")
                st.markdown("✔️ Vote Reset: " + ["No" if voted == True else "Yes"][0])
#                 st.markdown("⚡ Voted Current Epoch: " + ["No" if votedcurrentepoch == False else "Yes"][0])

        # Note
        st.markdown("#")
        st.markdown("#")
        st.caption(
            """
    NFA, DYOR -- This web app is in beta, I am not responsible for any information on this page.
            
    USD Value is just an estimate of CHR Price pulled from Firebird API.
            
    :red[If "Vote Reset" is No you cannot sell your veCHR unless you reset your vote.]
    
    :violet[If you found this useful you can buy me aka ALMIGHTY ABE a :coffee: at 0xc43521b72e0b7118d88ed29960036fb99cdad94a]
            """
        )

    except Exception as e:
        print(e)
        st.markdown("Error Please Try Again")

# Address Search
if selection == "Address":

    # URL Param Check
    try:
        if wallet_address:
            pass
    except:
        wallet_address = st.text_input(
        label="Your wallet address",
        placeholder="Enter your wallet address",
        max_chars=42,
    )

    if wallet_address:
        # Read Data
        try:
            # Checksum Address
            wallet_address = Web3.to_checksum_address(wallet_address)

            # veCHR Owner
            tokenids = []
            for index in range(100):
                veCHR = contract_instance1.functions.tokenOfOwnerByIndex(wallet_address, index).call()
                if veCHR > 0:
                    tokenids.append(veCHR)
                else:
                    break

            # veCHR DF
            tokendata = []
            for tokenid in tokenids:
                # Balance veCHR
                bal = round(
                    contract_instance1.functions.balanceOfNFT(tokenid).call() / 1000000000000000000,
                    4,
                )

                # Locked veCHR
                locked = round(
                    contract_instance1.functions.locked(tokenid).call()[0] / 1000000000000000000,
                    4,
                )

                # Lock End Date
                lockend = time.strftime(
                    "%Y-%m-%d",
                    time.gmtime(int(contract_instance1.functions.locked(tokenid).call()[1])),
                )

                # Voted Last Epoch
                voted = contract_instance1.functions.voted(tokenid).call()

                # Voted Current Epoch
#                 votedcurrentepoch = contract_instance2.functions.lastVoted(tokenid).call() > currentepoch

                tokendata.append(
                    {
                        "🔢 Token ID": tokenid,
                        "🔒 Locked CHR": locked,
                        "🧾 veCHR Balance": bal,
                        "🤑 Estimated USD Value": round(CHR_price * locked, 4),
                        "⏲️ Lock End Date": lockend,
                        "🗳️ Vote Share %": round(bal / totalSupply * 100, 4),
                        "✔️ Vote Reset": ["No" if voted == True else "Yes"][0],
#                         "⚡ Voted Current Epoch": ["No" if votedcurrentepoch == False else "Yes"][0],
                    }
                )

            veCHR_df = pd.DataFrame(tokendata)
            veCHR_df.sort_values(by="🔢 Token ID", axis=0, inplace=True)

            # creating a single-element container
            placeholder = st.empty()

            # Empty Placeholder Filled
            with placeholder.container():
                if wallet_address:
                    st.dataframe(veCHR_df)

            # Note
            st.markdown("#")
            st.markdown("#")
            st.caption(
                """
        NFA, DYOR -- This web app is in beta, I am not responsible for any information on this page.
                
        BUSD Value is just an estimate of CHR Price pulled from Firebird API.
                
        :red[If "Vote Reset" is No you cannot sell your veCHR unless you reset your vote.]
        
        :violet[If you found this useful you can buy me aka ALMIGHTY ABE a :coffee: at 0xc43521b72e0b7118d88ed29960036fb99cdad94a]
                """
            )

        except Exception as e:
            print(e)
            st.markdown("Error Please Try Again")
