#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
insfollow v3.0 - Instagram Follow/Unfollow Bot
Author: Instagram Bot Community
Date: 2026
Description: Simple Instagram bot to manage followers
"""

import os
import sys
import time
import random
import json
import getpass
from datetime import datetime

# Try to import required libraries
try:
    from instagrapi import Client
    from instagrapi.exceptions import ClientError, RateLimitError, LoginRequired
    import requests
except ImportError:
    print("\033[91m[!] Required libraries not found!\033[0m")
    print("\033[93m[*] Installing instagrapi...\033[0m")
    os.system("pip install instagrapi requests")
    print("\033[92m[✓] Installation complete. Please run the script again.\033[0m")
    sys.exit()

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Configuration
SESSION_FILE = "insfollow_session.json"
FOLLOW_LOG = "followed_users.txt"
UNFOLLOW_LOG = "unfollowed_users.txt"
DELAYS = (45, 120)  # Min/max seconds between actions


class InsFollow:
    """Main Instagram bot class"""
    
    def __init__(self):
        self.client = None
        self.user_id = None
        self.username = None
        self.followers = []
        self.following = []
        self.non_followers = []
        
    def banner(self):
        """Display cool banner"""
        os.system("clear" if os.name == "posix" else "cls")
        print(f"""
{BLUE}╔══════════════════════════════════════════════════════════╗
║{CYAN}   ██╗███╗   ██╗███████╗███████╗ ██████╗ ██╗     ██╗      {BLUE}║
║{CYAN}   ██║████╗  ██║██╔════╝██╔════╝██╔═══██╗██║     ██║      {BLUE}║
║{CYAN}   ██║██╔██╗ ██║███████╗█████╗  ██║   ██║██║     ██║      {BLUE}║
║{CYAN}   ██║██║╚██╗██║╚════██║██╔══╝  ██║   ██║██║     ██║      {BLUE}║
║{CYAN}   ██║██║ ╚████║███████║██║     ╚██████╔╝███████╗███████╗ {BLUE}║
║{CYAN}   ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝      ╚═════╝ ╚══════╝╚══════╝ {BLUE}║
║{YELLOW}              Instagram Follow/Unfollow Bot v3.0            {BLUE}║
║{RED}                      [FOR EDUCATIONAL USE ONLY]               {BLUE}║
╚══════════════════════════════════════════════════════════╝{RESET}
        """)
    
    def login(self):
        """Login to Instagram"""
        print(f"\n{YELLOW}[*] Instagram Login{RESET}")
        print("-" * 40)
        
        # Get credentials
        self.username = input(f"{CYAN}[?] Username: {RESET}").strip()
        password = getpass.getpass(f"{CYAN}[?] Password: {RESET}")
        
        self.client = Client()
        
        # Try to load existing session
        if os.path.exists(SESSION_FILE):
            try:
                print(f"{YELLOW}[*] Loading saved session...{RESET}")
                self.client.load_settings(SESSION_FILE)
                self.client.login(self.username, password)
                self.user_id = self.client.user_id
                print(f"{GREEN}[✓] Logged in using saved session!{RESET}")
                return True
            except:
                print(f"{YELLOW}[!] Session expired. Logging in fresh...{RESET}")
        
        # Fresh login
        try:
            print(f"{YELLOW}[*] Logging in as @{self.username}...{RESET}")
            self.client.login(self.username, password)
            self.client.dump_settings(SESSION_FILE)
            self.user_id = self.client.user_id
            print(f"{GREEN}[✓] Login successful!{RESET}")
            return True
        except Exception as e:
            print(f"{RED}[✗] Login failed: {e}{RESET}")
            return False
    
    def get_stats(self):
        """Get follower/following stats"""
        print(f"\n{YELLOW}[*] Fetching your account data...{RESET}")
        
        try:
            # Get followers
            print(f"{YELLOW}[*] Getting followers list...{RESET}")
            followers_dict = self.client.user_followers(self.user_id, amount=0)
            self.followers = list(followers_dict.values())
            
            # Get following
            print(f"{YELLOW}[*] Getting following list...{RESET}")
            following_dict = self.client.user_following(self.user_id, amount=0)
            self.following = list(following_dict.values())
            
            # Calculate non-followers
            follower_usernames = {f.username for f in self.followers}
            self.non_followers = [
                {"username": f.username, "pk": f.pk, "full_name": f.full_name}
                for f in self.following 
                if f.username not in follower_usernames
            ]
            
            # Display stats
            print(f"\n{GREEN}[✓] Stats for @{self.username}{RESET}")
            print(f"{CYAN}├─ Followers: {len(self.followers)}{RESET}")
            print(f"{CYAN}├─ Following: {len(self.following)}{RESET}")
            print(f"{CYAN}└─ Non-followers: {len(self.non_followers)}{RESET}")
            
            return True
            
        except Exception as e:
            print(f"{RED}[✗] Error fetching data: {e}{RESET}")
            return False
    
    def follow_users(self, target_username=None, count=20):
        """Follow users from target account's followers"""
        if not target_username:
            target_username = input(f"{CYAN}[?] Target username to steal followers from: {RESET}").strip()
        
        try:
            print(f"{YELLOW}[*] Getting followers of @{target_username}...{RESET}")
            
            # Get target user ID
            target_id = self.client.user_id_from_username(target_username)
            
            # Get their followers
            followers_dict = self.client.user_followers(target_id, amount=200)
            targets = list(followers_dict.values())
            
            print(f"{GREEN}[✓] Found {len(targets)} potential users to follow{RESET}")
            
            # Get users we already follow
            following_usernames = {f.username for f in self.following}
            
            # Filter out users we already follow
            new_targets = [t for t in targets if t.username not in following_usernames][:count]
            
            if not new_targets:
                print(f"{YELLOW}[!] No new users to follow{RESET}")
                return
            
            print(f"\n{YELLOW}[*] Starting to follow {len(new_targets)} users...{RESET}")
            print("-" * 40)
            
            successful = 0
            for i, user in enumerate(new_targets, 1):
                try:
                    # Check if private (skip)
                    if user.is_private:
                        print(f"{YELLOW}[{i}/{len(new_targets)}] Skipping @{user.username} (private account){RESET}")
                        continue
                    
                    print(f"{CYAN}[{i}/{len(new_targets)}] Following @{user.username}...{RESET}")
                    
                    # Follow the user
                    self.client.follow(user.pk)
                    
                    # Log the follow
                    with open(FOLLOW_LOG, 'a') as f:
                        f.write(f"{datetime.now()} - @{user.username}\n")
                    
                    successful += 1
                    print(f"{GREEN}    ✓ Success!{RESET}")
                    
                    # Random delay
                    if i < len(new_targets):
                        delay = random.randint(DELAYS[0], DELAYS[1])
                        print(f"{YELLOW}    Sleeping for {delay} seconds...{RESET}")
                        time.sleep(delay)
                        
                except RateLimitError:
                    print(f"{RED}[!] Rate limit hit! Stopping for now.{RESET}")
                    break
                except Exception as e:
                    print(f"{RED}    ✗ Failed: {str(e)[:50]}{RESET}")
            
            print(f"\n{GREEN}[✓] Followed {successful} users successfully!{RESET}")
            
        except Exception as e:
            print(f"{RED}[✗] Error: {e}{RESET}")
    
    def unfollow_non_followers(self, count=30):
        """Unfollow users who don't follow back"""
        if not self.non_followers:
            self.get_stats()
        
        if not self.non_followers:
            print(f"{GREEN}[✓] Everyone follows you back! Nice!{RESET}")
            return
        
        to_unfollow = self.non_followers[:count]
        print(f"\n{YELLOW}[*] Preparing to unfollow {len(to_unfollow)} users...{RESET}")
        
        # Show preview
        print(f"\n{CYAN}First 5 non-followers:{RESET}")
        for i, user in enumerate(to_unfollow[:5], 1):
            print(f"  {i}. @{user['username']}")
        
        confirm = input(f"\n{CYAN}[?] Continue with unfollow? (y/n): {RESET}").lower()
        if confirm != 'y':
            print(f"{YELLOW}[!] Cancelled{RESET}")
            return
        
        print(f"\n{YELLOW}[*] Starting unfollow...{RESET}")
        print("-" * 40)
        
        successful = 0
        for i, user in enumerate(to_unfollow, 1):
            try:
                print(f"{CYAN}[{i}/{len(to_unfollow)}] Unfollowing @{user['username']}...{RESET}")
                
                # Unfollow
                self.client.unfollow(user['pk'])
                
                # Log
                with open(UNFOLLOW_LOG, 'a') as f:
                    f.write(f"{datetime.now()} - @{user['username']}\n")
                
                successful += 1
                print(f"{GREEN}    ✓ Unfollowed!{RESET}")
                
                # Random delay
                if i < len(to_unfollow):
                    delay = random.randint(DELAYS[0], DELAYS[1])
                    print(f"{YELLOW}    Sleeping for {delay} seconds...{RESET}")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"{RED}    ✗ Failed: {str(e)[:50]}{RESET}")
        
        print(f"\n{GREEN}[✓] Unfollowed {successful} users!{RESET}")
    
    def mass_unfollow(self, count=50):
        """Mass unfollow (use with caution)"""
        if not self.following:
            self.get_stats()
        
        to_unfollow = self.following[:count]
        
        print(f"{RED}{'='*50}{RESET}")
        print(f"{RED}[!] WARNING: Mass unfollow can get your account flagged!{RESET}")
        print(f"{RED}[!] Proceed only if you know what you're doing.{RESET}")
        print(f"{RED}{'='*50}{RESET}")
        
        print(f"\n{YELLOW}[*] Will attempt to unfollow {len(to_unfollow)} users{RESET}")
        
        confirm = input(f"{CYAN}[?] Type 'YES' to confirm: {RESET}")
        if confirm != 'YES':
            print(f"{YELLOW}[!] Cancelled{RESET}")
            return
        
        print(f"\n{YELLOW}[*] Starting mass unfollow...{RESET}")
        
        successful = 0
        for i, user in enumerate(to_unfollow, 1):
            try:
                print(f"{CYAN}[{i}/{len(to_unfollow)}] Unfollowing @{user.username}...{RESET}")
                self.client.unfollow(user.pk)
                successful += 1
                
                # Longer delays for mass unfollow
                time.sleep(random.randint(60, 180))
                
            except Exception as e:
                print(f"{RED}    ✗ Failed{RESET}")
        
        print(f"{GREEN}[✓] Mass unfollow complete: {successful} users{RESET}")
    
    def save_data(self):
        """Save follower data to JSON"""
        data = {
            "username": self.username,
            "timestamp": str(datetime.now()),
            "followers_count": len(self.followers),
            "following_count": len(self.following),
            "non_followers_count": len(self.non_followers),
            "non_followers": self.non_followers[:50]  # Save first 50
        }
        
        with open(f"{self.username}_data.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"{GREEN}[✓] Data saved to {self.username}_data.json{RESET}")
    
    def menu(self):
        """Main menu loop"""
        while True:
            print(f"""
{BOLD}{CYAN}┌───────────────────── MENU ─────────────────────┐{RESET}
{BLUE}1.{RESET} 📊 Show account stats
{BLUE}2.{RESET} 👥 Show non-followers list
{BLUE}3.{RESET} 🚀 Follow users (from target account)
{BLUE}4.{RESET} 🔄 Unfollow non-followers
{BLUE}5.{RESET} ⚠️  Mass unfollow (use with caution!)
{BLUE}6.{RESET} 💾 Save data to JSON
{BLUE}7.{RESET} 🚪 Exit
{BOLD}{CYAN}└──────────────────────────────────────────────────┘{RESET}
            """)
            
            choice = input(f"{CYAN}[?] Select option (1-7): {RESET}").strip()
            
            if choice == '1':
                self.get_stats()
                
            elif choice == '2':
                if not self.non_followers:
                    self.get_stats()
                
                print(f"\n{YELLOW}[*] Non-followers ({len(self.non_followers)}):{RESET}")
                for i, user in enumerate(self.non_followers[:20], 1):
                    print(f"  {i}. @{user['username']}")
                
            elif choice == '3':
                target = input(f"{CYAN}[?] Target username (or press Enter for 'nasa'): {RESET}").strip()
                target = target if target else "nasa"
                
                try:
                    count = int(input(f"{CYAN}[?] How many to follow? (max 30): {RESET}") or "20")
                    count = min(count, 30)
                except:
                    count = 20
                
                self.follow_users(target, count)
                
            elif choice == '4':
                try:
                    count = int(input(f"{CYAN}[?] How many to unfollow? (max 30): {RESET}") or "20")
                    count = min(count, 30)
                except:
                    count = 20
                
                self.unfollow_non_followers(count)
                
            elif choice == '5':
                try:
                    count = int(input(f"{CYAN}[?] How many to mass unfollow? (max 100): {RESET}") or "50")
                    count = min(count, 100)
                except:
                    count = 50
                
                self.mass_unfollow(count)
                
            elif choice == '6':
                self.save_data()
                
            elif choice == '7':
                print(f"\n{GREEN}[✓] Goodbye! 👋{RESET}")
                sys.exit()
                
            else:
                print(f"{RED}[!] Invalid option{RESET}")
            
            input(f"\n{YELLOW}[*] Press Enter to continue...{RESET}")


def main():
    """Main function"""
    bot = InsFollow()
    bot.banner()
    
    # Login
    if not bot.login():
        print(f"{RED}[!] Login failed. Exiting...{RESET}")
        sys.exit(1)
    
    # Get initial stats
    bot.get_stats()
    
    # Show menu
    bot.menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Interrupted by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{RED}[!] Unexpected error: {e}{RESET}")
        sys.exit(1)
