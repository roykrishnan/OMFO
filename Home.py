import streamlit as st
from streamlit_extras.app_logo import add_logo  # Import the app_logo function

#Use the app_logo function to display the logo
add_logo("images/liquid_logo.png", height=65)
st.sidebar.image("images/small_logo.png",caption="Developed and Maintained by Roy Krishnan")


# Rest of your Streamlit code
st.title("The One Man Front Office | OMFO")
st.subheader("By: Roy Krishnan")
st.markdown("**Liquid Pro Am** [here](https://twitter.com/LiquidProAm_) | **Roy's personal X Account** [here](https://twitter.com/RoyKrishnan_) | **Roy's 2K Esports X (rarely checked these days)** [here](https://twitter.com/RoyKhris)") 
st.subheader('', divider='grey')

st.write("Where we'll release news, new releases, and updates: ")
st.link_button('OMFO X Account', 'https://twitter.com/1ManFrontOffice')

with st.expander("**What is OMFO?**"):
    st.write("**OMFO is a 2K League basketball player box-score score visualization system that allows teams to see real time rendered visualizations to track player progress and value**.") 
with st.expander("**Why build this?**"):
    st.markdown(""" 
            I broke into the NBA 2K League at 22, a month after I graduated college and after I founded my company Liquid Sports Lab and our NBA 2K Team Liquid Pro Am in January 2021. 
            Liquid Pro Am was always just supposed to be an experiment of what analytics could do in e-sports, but instead it became part of my way to break into the NBA. 
            After a stint as an Assistant Coach and the Offensive Co-Ordinator with the Dallas Mavericks and Mavs Gaming, I became the GM and Head Coach of the Toronto Raptors' - Raptors Uprising in 2023 where statistical thinking
            became my leverage point in systematically engineering an honest rebuild plan to be a playoff contender in two years. 
            
            The global problem? Objectivity is not always invested in, simply because the 2K League internal ecosystem is too small and therefore has to run like a startup, where every dollar counts.
            Even if you invested in engineering, the $200,000 an organization would have to spend on talented help and a multi-faceted front office wouldn't be able to be marginally regenerated (in terms of profit) even if the players won every tournament.
            As a result, all front office operations are a one or two man job; all good coaches end up working 10-12 hour days and usually 6-7 days a week and therefore information is often forced to the backseat just because so much more needs to be done.
            
            Therefore, I created the One Man Front Office. A reflection of my time and thinking in the NBA 2K League in an effort to bring more information to the 2KL staff, player, fan or analyst's pocket. 
            This game will always be played by players, and the analytics are not here to prove a point, they are here to keep each and all honest about who they are today and how they can
            be the best version of themselves tomorrow.  
             """)

with st.expander("**Accuracy**"):
    st.write('OMFO is run off of source data publicly available from the 2K League. All scrapes and sorts come from what is issued, posted, and circulated by the league.')
with st.expander("App Limitations "):
    st.write("OMFO currently only contains Season 6 5v5 Data, there hasn't been enough of a basis in 3v3 over two years to provide a true definition of 'good' yet.")
    st.write("Furthermore, the 3v3 data collection publicly available at the moment is not the most reliable. This is something we're hoping to address in our Season 7 release.")
with st.expander("**Premium Model**"):
    st.write("""
            As soon as Season 7 starts, we'll be shifting towards a $199/month model to provide more information and the translation between 
            amateur 2K and professional 2K, we'll be able to answer questions like 'how do you know amateur talent is going to translate to the league?'
            
            We'll have: 
            - Rotation Percentages (How often does each team Stack/Triangle/Circle etc.?)
            - Off-Ball Defender status (Who do you want switched on ball?)
            - PG Habits: What are the opposing PG's tendencies?
                - For example: in the Turn Tournament last year one PG has shot 20 fades in 5v5: 17 fades from the left wing, 3 from the right wing. He 10/17 on the left fade, 0/3 going right. My team forced him to fade to the right (his off hand) every time we played him (knowing he wouldn't).

            For $199 a month, your organization can have a data dashboard that allows you to dynamically ask questions and get answers in real time. We function as that Assistant Coach with all the numbers, displayed in perfect reporting to get your gameplan to that next level. 
             
             
             """)
    st.write('- Explanations (like the above) on how to actually use analytics to get positive outcomes for your team')
with st. expander("**You want to be in the 2K League? Here's five things you need to know:**"):
    st.write("""
            There's hopefully going to be a lot of players/analysts/hopeful coaches using this app. I want to *very transparent* with you just because I wish someone was with me and was once you myself. 
            Being in the league is *EXPONENTIALLY* harder than you think. I cannot stress enough how much your mental health will be tested, therefore you can also put yourself first by knowing the following.

            1. Pick an organization that reflects your interests (eg. if your #1 priority is the Business of Esports try to get in with an org that values business). If your 
             values don't reflect the organization's you're going to constantly feel frustrated and like there is way more to be done. You simply will not feel fulfilled if your #1 goal is winning (for example) and you don't feel like the organization's decision making reflects that.

            2. There's an art to corporate, be familiar with it. Hiring decisions are made by those in upper management, not by how many vouches you have on X. Being a great coach and a bad interviewer will get you nothing.
             
            3. Know exactly where you bring value. In one sentence be able to convey what you bring to the table that someone else either cannot, or cannot at your level.
             
            4. The only reason you should be doing this job is because you love it. If you are using the 2K League as a resume builder I promise you it will not usually work (unless that other thing you want to do is also in Esports).
            
            5.  Keep perspective. **The most important thing I can tell you**: every time you have a bad day, take deep breath, collect your emotions and remind yourself of why you do this in the first place, the fact that a younger you would not believe
             the fact you get to do this for a living. The second it stops feeling like a passion and starts feels like a chore is the first sign that its time to graciously and gracefully move on to what
             else life has to offer. 
            """)
