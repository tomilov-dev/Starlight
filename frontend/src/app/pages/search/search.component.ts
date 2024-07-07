import { Component } from '@angular/core';
import { IMDbMovieBase } from '../../models/base.movie.model';
import { IMDbPersonBase } from '../../models/person.model';
import { DataService } from '../../services/data.service';

enum SearchType {
  MOVIES = 'Фильмы',
  PERSONS = 'Людей',
}

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrl: './search.component.css',
})
export class SearchComponent {
  public SearchType = SearchType;

  searchType: SearchType = this.SearchType.MOVIES;
  searchQuery: string = '';

  placeholder: string = 'Властелин Колец...';
  placeholders: Map<SearchType, string> = new Map([
    [SearchType.MOVIES, 'Властелин Колец...'],
    [SearchType.PERSONS, 'Morgan Freeman'],
  ]);

  movies: IMDbMovieBase[] = [];
  persons: IMDbPersonBase[] = [];

  constructor(private dataService: DataService) {}

  updatePlaceholder() {
    this.placeholder = this.placeholders.get(this.searchType) || '';
  }

  search(): void {
    if (this.searchType && this.searchQuery) {
      if (this.searchType === SearchType.MOVIES) {
        this.dataService.searchMovies(this.searchQuery).subscribe((movies) => {
          console.log(movies);
          this.movies = movies;
        });
      } else if (this.searchType === SearchType.PERSONS) {
        this.dataService
          .searchPersons(this.searchQuery)
          .subscribe((persons) => {
            console.log(persons);
            this.persons = persons;
          });
      }
    }
  }

  setSearchType(settedSearchType: SearchType): void {
    this.searchType = settedSearchType;
  }
}
